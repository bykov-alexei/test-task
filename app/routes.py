from app import app
from app.models import File, Price, process_file

import os
import json
import plotly
import plotly.express as px
from uuid import uuid4 as uuid
from flask import request, render_template, redirect, abort
from peewee import DoesNotExist


@app.route('/')
def index():
    """Main page used for uploading .csv or .xlsx file
        ---
        produces:
          - text/html
        responses:
          200:
            description: HTML page with form for uploading a file
    """
    return render_template('index.html')


@app.route('/upload', methods=['post'])
def upload():
    """Uploads .csv or .xlsx file
        ---
        consumes:
          - multipart/form-data
        parameters:
          - name: file
            description: csv or xlsx file
            in: formData
            type: file
            required: true
        produces:
          - text/html
        responses:
          200:
            description: File was saved to server, client was redirected to queries page
    """
    file = request.files.get('file')
    filename = str(uuid())
    file.save(os.path.join('static', filename))

    file_object = File(name=file.filename, path=filename, status='uploaded')
    file_object.save()

    process_file.delay(file_object.id)

    return redirect('/queries')


@app.route('/queries')
def queries_page():
    """Page with all listed queries
            ---
            produces:
              - text/html
            responses:
              200:
                description: HTML page used for tracking processing queries
        """
    queries = list(File.select())
    return render_template('queries.html', queries=queries)


@app.route('/query/<int:id>/delete')
def delete_query(id):
    """Deletes query
        ---
        parameters:
          - name: id
            description: query id
            in: path
            type: integer
            required: true
        produces:
          - text/html
        responses:
          200:
            description: Query was deleted, client was redirected to queries page
          404:
            description: Query was not found
    """
    try:
        file = File.get_by_id(id)
    except DoesNotExist:
        return abort(404)

    Price.delete().where(Price.file == file).execute()
    File.delete().where(File.id == id).execute()
    return redirect('/queries')


@app.route('/plot/<int:id>')
def plot_page(id):
    """Page with price and seasonality charts
            ---
            parameters:
              - name: id
                description: query id
                in: path
                type: integer
                required: true
            produces:
              - text/html
            responses:
              200:
                description: HTML page with plotly charts
              404:
                description: Plots for specified query id was not found
        """
    try:
        df = Price.get_file_dataframe(id)
    except DoesNotExist as e:
        return abort(404)

    price_df = df[['date', 'open', 'high', 'low', 'close']].melt('date')
    price_plot = px.line(price_df, x='date', y='value', color='variable')
    price_plot_json = json.dumps(price_plot, cls=plotly.utils.PlotlyJSONEncoder)

    seasonality_df = df[['date', 'open_seasonality', 'high_seasonality', 'low_seasonality', 'close_seasonality']].melt('date')
    seasonality_plot = px.line(seasonality_df, x='date', y='value', color='variable')
    seasonality_plot_json = json.dumps(seasonality_plot, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('plot.html', price_plot_json=price_plot_json, seasonality_plot_json=seasonality_plot_json)
