from django.db import models


class Room(models.Model):
    title = models.CharField(max_length=255)
    staff_only = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def group_name(self):
        return "room-%s" % self.id
