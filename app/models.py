import flask_sqlalchemy

db = flask_sqlalchemy.SQLAlchemy()


class Events(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.String(100), primary_key=True)
    asin = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    source = db.Column(db.String(50))
    stars = db.Column(db.Integer)
    timestamp = db.Column(db.TIMESTAMP)

    def __repr__(self):
        return f"<Event ('{self.id}')>"
