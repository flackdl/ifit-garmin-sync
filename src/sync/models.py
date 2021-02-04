from django.db import models


class Workout(models.Model):
    name = models.CharField(max_length=500)
    date_created = models.DateTimeField(unique=True)
    date_synced = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return '{} [{}]'.format(self.name, self.date_created.isoformat())
