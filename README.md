# Export iFit workouts to Garmin Connect

This is a web application which syncs your iFit workouts to your Garmin Connect account.

It runs a scheduled background task to run every few hours.

## Run

You'll need **docker** and **docker-compose** installed to run everything. 

You'll be required to define the following variables in the file `.env`:

- *IFIT_USER*
- *IFIT_PASS*
- *GARMIN_USER*
- *GARMIN_PASS*

Copy the `env.template file` to `.env`:
    
    cp env.template .env

Populate the environment variables in `.env` then start up everything with:

    docker-compose up -d --build

You should now be able to access the dashboard at http://localhost:8080.

Sync tasks run automatically every few hours (configurable in `SYNC_HOURS` env var) but you can force the task in the dashboard as well.

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
