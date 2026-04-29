import requests
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    name = models.CharField(max_length=25, blank=True, null=True)
    avatar_url = models.URLField(max_length=1000, null=True)

    def __str__(self):
        return self.username
