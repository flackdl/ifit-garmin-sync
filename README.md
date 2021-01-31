# Export iFit workouts to Garmin Connect

Software:

- python 3 
- Django 3
- lxml
- [Garmin-uploader](https://github.com/La0/garmin-uploader)

Install

    python3 -mvenv ~/.envs/ifit-sync
    activate ~/.envs/ifit-sync/bin/activate
    pip install -r src/requirements.txt

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
