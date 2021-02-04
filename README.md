# Export iFit workouts to Garmin Connect

This is a web application which syncs your iFit workouts to your Garmin Connect account.

It runs a scheduled background task to run every few hours.

### Deploy for free to Heroku:

You can run this app for free on Heroku.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Make sure to define the following [Config Vars](https://devcenter.heroku.com/articles/config-vars#using-the-heroku-dashboard) in Heroku's *Settings* once you've created your account:

    IFIT_USER = xxx
    IFIT_PASS = xxx
    GARMIN_USER = xxx
    GARMIN_PASS = xxx

Swap *YOUR-IFIT-APP-NAME* with your new heroku app and visit: https://YOUR-IFIT-APP-NAME.herokuapp.com/

### Development

Software:

- python 3 
- Django 3
- lxml
- celery
- [Garmin-uploader](https://github.com/La0/garmin-uploader)


Install

    python3 -mvenv ~/.envs/ifit-sync
    activate ~/.envs/ifit-sync/bin/activate
    pip install -r requirements.txt

Redis:

You need redis running for the task queue.  I use docker to make that part easy.

    docker-compose up -d redis
    
Configure

    export IFIT_USER = xxx
    export IFIT_PASS = xxx
    export GARMIN_USER = xxx
    export GARMIN_PASS = xxx

Run web app

    activate ~/.envs/ifit-sync/bin/activate
    python src/manage.py migrate
    python src/manage.py runserver

Run celery (task queue)

    celery --workdir src --app sync worker --beat --loglevel INFO
