# Export iFit workouts to Garmin Connect

This is a web application which syncs your iFit workouts to your Garmin Connect account.

It runs a scheduled background task to run every few hours.

### Deploy for free to Heroku:

You can run this app for free on Heroku.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

You'll be required to define the following variables during the installation in Heroku:

- *IFIT_USER*
- *IFIT_PASS*
- *GARMIN_USER*
- *GARMIN_PASS*

##### Schedule syncs

The free apps on Heroku automatically sleep after 30 minutes of inactivity, so, to automatically sync your workouts,
you'll need to schedule a recurring job to sync your workouts.  Set up a *Heroku Scheduler* job and create a new recurring job like the following:

    curl https://YOUR-APP-NAME.herokuapp.com/workouts/export

**Make sure to replace `YOUR-APP-NAME` with your heroku app name.**

This will make sure it syncs daily/hourly automatically for you.

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
