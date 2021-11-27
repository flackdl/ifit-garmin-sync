import os
import tempfile
import logging
import requests
from datetime import datetime

from django.db import IntegrityError
from django.utils.dateparse import parse_datetime
from garmin_uploader.user import User
from garmin_uploader.workflow import Activity
from lxml import html, etree
from django.core.cache import cache
from django.conf import settings
from requests import HTTPError
from requests.cookies import cookiejar_from_dict

from sync.models import Workout

CACHE_KEY_IFIT = 'ifit-cookies'
IFIT_URL_AUTH = 'https://www.ifit.com/web-api/login'
IFIT_URL_WORKOUTS = 'https://www.ifit.com/me/workouts'
IFIT_URL_EXPORT_WORKOUT = 'https://www.ifit.com/workout/export/tcx/'


class SyncProcessor:
    session = None
    message = None

    def __init__(self):
        self._setup_session()

    def process(self, retry=True):
        # auth
        if not self.session.cookies:
            logging.info('no cached session, authenticating')
            self._auth()
        try:
            workout_urls = self._workouts_urls()
        except HTTPError:
            self._reset_session()
            if retry:
                return self.process(retry=False)
            self.message = 'failed getting workouts'
            return False

        paths_exported = self._export(workout_urls)
        self._import(paths_exported)

        return True

    def _export(self, workout_urls: list):
        workouts = []
        for url in workout_urls:
            workout_id = os.path.basename(url)
            if Workout.objects.filter(ifit_id=workout_id).exists():
                logging.info('skipping workout {} that has already been synced'.format(workout_id))
                continue
            response = self.session.get(os.path.join(IFIT_URL_EXPORT_WORKOUT, workout_id))
            logging.info(response.url)
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.tcx') as fd:
                fd.write(response.text)
                workouts.append({
                    'path': fd.name,
                    'id': workout_id,
                })
        logging.info('exported:')
        logging.info(workouts)
        return workouts

    def _import(self, workouts: list):
        if not workouts:
            return []
        titles = []
        user = User(username=settings.GARMIN_USER, password=settings.GARMIN_PASS)
        if not user.authenticate():
            logging.error('could not authenticate with garmin')
            raise Exception('could not authenticate with garmin')
        namespaces = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
        # save logs for imported workouts
        for workout in workouts:
            # TODO - set <Activity Sport="">  Other|Running|Biking
            tree = etree.parse(workout['path'])
            notes = tree.xpath('//ns:Activity/ns:Notes/text()', namespaces=namespaces)
            date = tree.xpath('//ns:Activity/ns:Id/text()', namespaces=namespaces)
            title = notes[0] if notes else 'Unknown Upload: {}'.format(datetime.now().isoformat())
            activity = Activity(path=workout['path'], name=title)
            activity.upload(user)
            titles.append(title)
            try:
                Workout.objects.create(
                    ifit_id=workout['id'],
                    name=title,
                    date_created=parse_datetime(date[0]) if date else datetime.now(),
                )
            except IntegrityError as e:
                logging.exception('skipping sync that generated an unknown database error')
                logging.error(str(e))
                continue

        logging.info('imported:')
        logging.info(titles)

        return titles

    def _cache_cookies(self, cookies) -> None:
        return cache.set(CACHE_KEY_IFIT, dict(cookies))

    def _reset_session(self) -> None:
        cache.delete(CACHE_KEY_IFIT)

    def _setup_session(self) -> None:
        self.session = requests.session()
        cached_cookies = cache.get(CACHE_KEY_IFIT)
        if cached_cookies:
            if self.session.cookies:
                self.session.cookies.update(cached_cookies)
            else:
                self.session.cookies = cookiejar_from_dict(cached_cookies)

    def _auth(self) -> None:
        response = self.session.post(
            IFIT_URL_AUTH, json={'email': settings.IFIT_USER, 'password': settings.IFIT_PASS})
        response.raise_for_status()
        self._cache_cookies(self.session.cookies)

    def _workouts_urls(self) -> list:

        # query workouts
        response = self.session.get(IFIT_URL_WORKOUTS)
        response.raise_for_status()

        # parse workouts
        tree = html.fromstring(response.content)
        return tree.xpath('//div[contains(@class, "workout-row")]/a/@href')
