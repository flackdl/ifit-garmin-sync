# Export iFit workouts to Garmin Connect

This is a web application which sync your iFit workouts to your Garmin Connect account.

### Deploy for free to Heroku:

You can run this app for free on Heroku.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Make sure to define the following `Config Vars` in *Settings* once you've created your account:

    IFIT_USER = xxx
    IFIT_PASS = xxx
    GARMIN_USER = xxx
    GARMIN_PASS = xxx

Next, set up the *Heroku Scheduler* and create a new recurring job:

    curl https://YOUR-APP-NAME.herokuapp.com/workouts/export

**Make sure to replace `YOUR-APP-NAME`.**

This will make sure it syncs daily/hourly automatically for you.

### Development

Software:

- python 3 
- Django 3
- lxml
- [Garmin-uploader](https://github.com/La0/garmin-uploader)

Install

    python3 -mvenv ~/.envs/ifit-sync
    activate ~/.envs/ifit-sync/bin/activate
    pip install -r requirements.txt

Configure

    export IFIT_USER = xxx
    export IFIT_PASS = xxx
    export GARMIN_USER = xxx
    export GARMIN_PASS = xxx

Run

    activate ~/.envs/ifit-sync/bin/activate
    python src/manage.py migrate
    python src/manage.py runserver

Visiting http://127.0.0.1:8000/workouts/export will export your iFit workouts to your Garmin Connect account.
