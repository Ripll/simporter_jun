import json
from flask import request

from . import create_app
from .models import Events, db
from .utils import get_possible_attrs, is_date
from datetime import datetime
app = create_app()


@app.route('/api/info', methods=['GET'])
def info():
    data = get_possible_attrs(db)
    return json.dumps(data)


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
            return json.dumps({"error": f"Not passed required parameter: {p_name}",
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
        elif request.args[filter] not in possible_attrs['values'][filter]:
            error = True
            error_msg = f"The {filter} can only take such values: {possible_attrs['values'][filter]}"
        else:
            filters[filter] = request.args[filter]
    if error:
        return json.dumps({"error": error_msg,
                           "result": False})

    db_result = db.engine.execute("""SELECT
                                        date_trunc('{}', timestamp) w,
                                        COUNT (*)
                                      FROM
                                        events
                                      WHERE timestamp >= '{}' AND timestamp <= '{}' {}
                                      GROUP BY
                                        w
                                      ORDER BY
                                        w;""".format('month' if grouping_data['Grouping'] == 'monthly' else 'week',
                                                     grouping_data['startDate'],
                                                     grouping_data['endDate'],
                                                     "AND ".join([f"{i} = '{j}'" for i, j in filters.items()])))
    result_timeline = []
    for row in db_result:
        result_timeline.append({"date": row[0].strftime('%Y-%m-%d'), "value": row[1]})

    return json.dumps({"timeline": result_timeline,
                       "result": True})




