from django.db import models
from django.contrib.auth.models import User


class Location(models.Model):
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()


class OnlineUser(models.Model):
    user = models.ForeignKey(User)
    reply_channel = models.TextField()


class Follower(models.Model):
    follower = models.ForeignKey(User, related_name='follower')
    followee = models.ForeignKey(User, related_name='followee')



