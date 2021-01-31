import os
import tempfile
import logging
import requests
from datetime import datetime
from garmin_uploader.user import User
from garmin_uploader.workflow import Activity
from lxml import html, etree
from django.core.cache import cache
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from requests import HTTPError
from requests.cookies import cookiejar_from_dict

CACHE_KEY_IFIT = 'ifit-cookies'
IFIT_URL_AUTH = 'https://www.ifit.com/web-api/login'
IFIT_URL_WORKOUTS = 'https://www.ifit.com/me/workouts'
IFIT_URL_EXPORT_WORKOUT = 'https://www.ifit.com/workout/export/tcx/'


class IfitWorkoutsExportView(View):
    session = None
    export = False

    def get(self, request, retry=True):
        self._setup_session()
        if not self.session.cookies:
            logging.info('no cached session, authenticating')
            try:
                self._auth()
            except HTTPError:
                return JsonResponse({'success': False, 'message': 'failed authenticating'})
        try:
            workout_urls = self._workouts_urls()
        except HTTPError:
            self._reset_session()
            if retry:
                return self.get(request, retry=False)
            return JsonResponse({'success': False, 'message': 'failed getting workouts'})

        response = {'workouts': workout_urls}

        if self.export:
            paths_exported = self._export(workout_urls)
            paths_imported = self._import(paths_exported)
            response.update(
                {'imported': paths_imported, 'exported': paths_exported})

        return JsonResponse(response)

    def _export(self, workout_urls: list):
        paths = []
        for url in workout_urls:
            workout_id = os.path.basename(url)
            response = self.session.get(os.path.join(IFIT_URL_EXPORT_WORKOUT, workout_id))
            logging.info(response.url)
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.tcx') as fd:
                fd.write(response.text)
                paths.append(fd.name)
        logging.info(paths)
        return paths

    def _import(self, paths: list):
        titles = []
        user = User(username=settings.GARMIN_USER, password=settings.GARMIN_PASS)
        user.authenticate()
        namespaces = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
        # find name of workouts
        for path in paths:
            tree = etree.parse(path)
            notes = tree.xpath('//ns:Activity/ns:Notes/text()', namespaces=namespaces)
            title = notes[0] if notes else 'Unknown Upload: {}'.format(datetime.now().isoformat())
            activity = Activity(path=path, name=title)
            activity.upload(user)
            titles.append(title)
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
