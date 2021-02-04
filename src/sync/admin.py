from django.contrib import admin
from sync.models import Workout


@admin.register(Workout)
class SettingsAdmin(admin.ModelAdmin):
    pass

