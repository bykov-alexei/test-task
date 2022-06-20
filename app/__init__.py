from config import db_config, celery_config

from celery import Celery
from flask import Flask
from flasgger import Swagger
from peewee import MySQLDatabase


def make_celery(app):
    celery = Celery(app.import_name)
    celery.conf.update(app.config["CELERY_CONFIG"])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


app = Flask(__name__)
db = MySQLDatabase(**db_config, field_types={'status': 'tinyint'})
app.config.update(CELERY_CONFIG=celery_config)
celery = make_celery(app)
swagger = Swagger(app)


from .routes import *
