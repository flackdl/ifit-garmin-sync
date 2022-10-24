python manage.py migrate
python manage.py createcachetable
gunicorn ifit.wsgi:application -b :80
