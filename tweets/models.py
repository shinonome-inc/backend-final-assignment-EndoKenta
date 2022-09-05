from django.conf import settings
from django.db import models
from django.utils import timezone


class Tweet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(default=timezone.now)
