from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from sync.models import Workout
from sync.tasks import sync


class HomeView(View):

    def get(self, request):
        workouts = Workout.objects.all()
        return render(request, 'index.html', {'workouts': workouts})


class ExportView(View):
    def get(self, request):
        sync.delay()
        return HttpResponse('Successfully queued sync task')
