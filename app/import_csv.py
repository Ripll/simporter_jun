import csv
from app.models import Events
import datetime


def import_test_data(db):
    with open('test_data.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        header = True
        for row in spamreader:
            if header:
                header = False
                continue
            new_event = Events(asin=row[0],
                               brand=row[1],
                               id=row[2],
                               source=row[3],
                               stars=int(row[4]),
                               timestamp=datetime.datetime.fromtimestamp(int(row[5])))
            db.session.add(new_event)
    db.session.commit()