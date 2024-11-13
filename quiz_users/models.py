from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    image_path = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username
