db_config = {
    'database': 'stocks',
    'user': 'stocks',
    'password': 'stocks',
    'host': 'mysql',
}
celery_config = {
    'broker_url': 'redis://redis:6379',
    'result_backend': 'redis://redis:6379',
}
