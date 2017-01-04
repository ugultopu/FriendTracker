from channels.auth import channel_session_user_from_http, channel_session_user
from channels import Group
from FriendTrackerApp.models import Location, OnlineUser, Follower
from .detlogging import detlog
import json


@channel_session_user_from_http
def location_connect(message):
    Group('online-users').add(message.reply_channel)


@channel_session_user
def location_receive(message):
    data = json.loads(message.content['text'])
    print(data)
    Group('online-users').send({
        'text': json.dumps(data)
    })


@channel_session_user
def location_send(message):
    detlog(message)


@channel_session_user
def location_disconnect(message):
    Group('online-users').remove(message.reply_channel)



