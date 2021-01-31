import logging
import requests
from lxml import html
from django.core.cache import cache
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from requests import HTTPError
from requests.cookies import cookiejar_from_dict

CACHE_KEY_IFIT = 'ifit-cookies'
IFIT_URL_AUTH = 'https://www.ifit.com/web-api/login'
IFIT_URL_WORKOUTS = 'https://www.ifit.com/me/workouts'


class IfitWorkoutsView(View):
    session = None

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

    def get(self, request, retry=True):
        self._setup_session()
        if not self.session.cookies:
            logging.info('no cached session, authenticating')
            try:
                self._auth()
            except HTTPError:
                return JsonResponse({'success': False, 'message': 'failed authenticating'})
        try:
            workouts = self._workouts()
        except HTTPError:
            self._reset_session()
            if retry:
                return self.get(request, retry=False)
            return JsonResponse({'success': False, 'message': 'failed getting workouts'})

        return JsonResponse({'workouts': workouts})

    def _workouts(self) -> list:

        # query workouts
        response = self.session.get(IFIT_URL_WORKOUTS)
        response.raise_for_status()

        # parse workouts
        tree = html.fromstring(response.content)
        return tree.xpath('//div[contains(@class, "workout-row")]/a/@href')
