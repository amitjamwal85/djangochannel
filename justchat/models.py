from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

from djangochannel import settings


class Room(models.Model):
    title = models.CharField(max_length=255)
    staff_only = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def group_name(self):
        return "room-%s" % self.id


MALE = "male"
FEMALE = "female"
GENDER = (
    (MALE, "male"),
    (FEMALE, "female")
)


def directory_path(self, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return "profile/{}".format(filename)


class User(AbstractUser):
    gender = models.CharField(choices=GENDER, max_length=10, null=False)
    profile_image = models.FileField(upload_to=directory_path)

    class Meta:
        db_table = "auth_user"

    @property
    def get_full_name(self):
        return "{} {}".format(self.first_name, self.last_name)


class ChatHistory(models.Model):
    a_party_user = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, related_name="a_party_user")
    b_party_user = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, related_name="b_arty_user")
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)







