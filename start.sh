python3 debug.py &
celery -A app.celery worker -f celery.logs &
wait