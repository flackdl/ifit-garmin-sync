web: gunicorn --chdir src ifit.wsgi --log-file -
worker: celery --workdir src --app sync worker --beat --loglevel INFO
