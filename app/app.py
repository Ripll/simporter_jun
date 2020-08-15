from flask import request, jsonify
from . import create_app
from .models import db
from .utils import get_possible_attrs, is_date
from datetime import datetime

app = create_app()


@app.route('/api/info', methods=['GET'])
def info():
    data = get_possible_attrs(db)
    data['result'] = True
    return jsonify(data)


@app.route('/api/timeline', methods=['GET'])
def timeline():
    required_params = ['startDate',
                       'endDate',
                       'Type',
                       'Grouping']

    # Check required parameters
    grouping_data = {}
    for p_name in required_params:
        if p_value := request.args.get(p_name):
            grouping_data[p_name] = p_value
        else:
            return jsonify({"error": f"Not passed required parameter: {p_name}",
                            "result": False})

    # Validation group fields
    possible_attrs = get_possible_attrs(db)
    error = False
    error_msg = ""
    if not is_date(grouping_data['startDate']) or not is_date(grouping_data['endDate']):
        error = True
        error_msg = "Error in startDate or endDate: date format must be %Y-%m-%d, for example: 2020-01-01"
    if datetime.strptime(grouping_data['startDate'], "%Y-%m-%d") > \
            datetime.strptime(grouping_data['endDate'], "%Y-%m-%d"):
        error = True
        error_msg = "endDate must be greater than startDate."
    if grouping_data['Type'] not in ["cumulative", "usual"]:
        error = True
        error_msg = "Type field must be in ['cumulative', 'usual']"
    if grouping_data['Grouping'] not in ['weekly', 'bi-weekly', 'monthly']:
        error = True
        error_msg = "Grouping field must be in ['weekly', 'bi-weekly', 'monthly']"

    # Validation filters
    filters = {}
    for filter in request.args.keys():
        if filter in required_params:
            continue
        elif filter not in possible_attrs['attributes']:
            error = True
            error_msg = f"Unexpected argument {filter}"
            break
        elif request.args[filter] not in [str(i) for i in possible_attrs['values'][filter]]:
            error = True
            error_msg = f"The {filter} can only take such values: {possible_attrs['values'][filter]}"
        else:
            filters[filter] = request.args[filter]
    if error:
        return jsonify({"error": error_msg,
                        "result": False})
    # Get timeline with weekly or monthly date_trunc
    db_result = db.engine.execute("""SELECT b.minute date, coalesce(a.cnt, 0) cnt
                                    FROM
                                      (SELECT date_trunc('{period}', TIMESTAMP) w,
                                              COUNT (*) AS cnt
                                       FROM EVENTS
                                       WHERE TIMESTAMP >= date_trunc('{period}', TIMESTAMP '{start}')
                                         AND TIMESTAMP <= '{end}' {filter_params}
                                       GROUP BY w
                                       ORDER BY w) a
                                    RIGHT JOIN
                                      (SELECT generate_series(date_trunc('{period}', TIMESTAMP '{start}'),
                                       TIMESTAMP '{end}', '1 {period}') AS MINUTE) b 
                                       ON b.minute = a.w"""
                                  .format(period='month' if grouping_data['Grouping'] == 'monthly' else 'week',
                                          start=grouping_data['startDate'],
                                          end=grouping_data['endDate'],
                                          filter_params="AND " + a if (a := "AND ".join([f"{i} = '{j}'"
                                                                                        for i, j in filters.items()]))
                                                        else ""))
    # formatting usual timeline
    result_timeline = []
    skip = False
    for row in db_result:
        # if bi-weekly = add value to previous tick
        if grouping_data['Grouping'] == 'bi-weekly' and skip:
            result_timeline[-1]['value'] += row[1]
            skip = False
        else:
            result_timeline.append({"date": row[0].strftime('%Y-%m-%d'), "value": row[1]})
            if grouping_data['Grouping'] == 'bi-weekly':
                skip = True

    # convert from usual to cumulative
    if grouping_data['Type'] == "cumulative":
        index = 0
        for i in result_timeline[1:]:
            i['value'] += result_timeline[index]['value']
            index += 1

    return jsonify({"timeline": result_timeline,
                    "result": True})




