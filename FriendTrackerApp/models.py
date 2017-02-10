from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.base_session import AbstractBaseSession
from django.db import models
from FriendTrackerApp.sessions import SessionStore


class Location(models.Model):
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()


class PinnedLocation(models.Model):
    user = models.ForeignKey(User)
    name = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='%(class)s_follower')
    followee = models.ForeignKey(User, related_name='%(class)s_followee')

class FollowRequest(models.Model):
    followee = models.ForeignKey(User, related_name='%(class)s_followee')
    follower = models.ForeignKey(User, related_name='%(class)s_follower')


class CustomSession(AbstractBaseSession):
    account_id = models.IntegerField(null=True, db_index=True)

    @classmethod
    def get_session_store_class(cls):
        return SessionStore


