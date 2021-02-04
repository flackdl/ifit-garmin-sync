from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from sync.models import Workout
from sync.tasks import sync


class HomeView(View):

    def get(self, request):
        if not all([settings.IFIT_USER, settings.IFIT_PASS, settings.GARMIN_USER, settings.GARMIN_PASS]):
            missing_settings = True
        else:
            missing_settings = False
        workouts = Workout.objects.all()
        return render(request, 'index.html', {'workouts': workouts, 'missing_settings': missing_settings})


class ExportView(View):
    def get(self, request):
        sync.delay()
        return HttpResponse('Successfully queued sync task')
