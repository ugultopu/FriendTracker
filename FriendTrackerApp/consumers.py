from channels.auth import channel_session_user_from_http, channel_session_user
from channels import Group
from FriendTrackerApp.models import Location, OnlineUser, Follower
from .detlogging import detlog
import json


@channel_session_user_from_http
def location_connect(message):
    user = OnlineUser(user=message.user, reply_channel=message.reply_channel)
    user.save()


@channel_session_user
def location_receive(message):
    #print(message.content['text']) # This is what is sent from the client
    data = json.loads(message.content['text'])

    timestamp = data['timestamp']
    latitude = data['latitude']
    longitude = data['longitude']

    location = Location(user=message.user, timestamp=timestamp, latitude=latitude, longitude=longitude)
    location.save()


@channel_session_user
def location_send(message):
    detlog(message)


@channel_session_user
def location_disconnect(message):
    user = OnlineUser.objects.get(user=message.user)
    user.delete()



