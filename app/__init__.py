from flask import Flask

from .models import db, Events
from . import config
from import_csv import import_test_data

def create_app():
    flask_app = Flask(__name__)
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.app_context().push()
    db.init_app(flask_app)
    db.create_all()
    if not db.session.query(Events).first():
        import_test_data(db)
    return flask_app
