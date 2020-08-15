from .models import Events
from datetime import datetime


def get_possible_attrs(db):
    attributes = [i.key for i in Events.__table__.columns if i.key not in ['id', 'timestamp']]
    values = {}
    for attr in attributes:
        values[attr] = [i.__dict__[attr] for i in Events.query.distinct(attr)]
    data = {
        "attributes": attributes,
        "values": values
    }
    return data


def is_date(x):
    try:
        datetime.strptime(x, "%Y-%m-%d")
        return True
    except:
        return False
