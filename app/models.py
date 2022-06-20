from app import db
from app import celery

import os
import pandas as pd
from peewee import Field, Model, CharField, FloatField, DateField, ForeignKeyField


class StatusField(Field):
    field_type = 'status'
    python_values = {
        0: 'uploaded',
        1: 'processing',
        2: 'ready',
        3: 'error',
    }

    def db_value(self, value):
        db_values = {k: i for i, k in StatusField.python_values.items()}
        return db_values[value]

    def python_value(self, value):
        return StatusField.python_values[value]


class File(Model):
    name = CharField()
    path = CharField()
    status = StatusField()

    class Meta:
        db_table = 'files'
        database = db


class Price(Model):
    date = DateField()
    file = ForeignKeyField(File)

    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()

    open_seasonality = FloatField()
    high_seasonality = FloatField()
    low_seasonality = FloatField()
    close_seasonality = FloatField()

    @staticmethod
    def get_file_dataframe(file_id):
        prices = Price.select().where(Price.file == File.get_by_id(file_id))
        df = pd.DataFrame(list(prices.dicts()))
        return df

    class Meta:
        db_table = 'prices'
        database = db


@celery.task()
def process_file(id):
    file = File.get_by_id(id)
    file.status = 'processing'
    file.save()

    filename = file.path

    try:
        try:
            data = pd.read_excel(os.path.join('static', filename))
        except UnicodeDecodeError as e:
            data = pd.read_csv(os.path.join('static', filename))
        data.columns = ['stock', 'date', 'open', 'high', 'low', 'close']
        data.date = pd.to_datetime(data.date)
        data = data.drop(columns=['stock'])

        year = data.groupby(data.date.dt.year).mean()

        data.index = data.date

        seasonality = data.drop(columns=['date']).apply(lambda row: row / year.loc[row.name.year], axis=1)
        seasonality.columns = ['open_seasonality', 'high_seasonality', 'low_seasonality', 'close_seasonality']
        data = pd.concat([data, seasonality], axis=1)

        prices = []
        for i, row in data.iterrows():
            dct = row.to_dict()
            dct.update({'file': file})
            prices.append(dct)
        Price.insert_many(prices).execute()

        file.status = 'ready'
        file.save()
    except Exception as e:
        print(e)
        file.status = 'error'
        file.save()
