from channels.auth import channel_session_user_from_http, channel_session_user
from channels import Group
from FriendTrackerApp.models import Location, OnlineUser, Follower
from django.contrib.sessions.models import Session
from .detlogging import detlog
import json


@channel_session_user_from_http
def location_connect(message):
    Group('online-users').add(message.reply_channel)
    message.reply_channel.send({'accept': True})


@channel_session_user
def location_receive(message):
    data = json.loads(message.content['text'])
    data['user'] = message.user.id
    # detlog(message.user)
    print(data)
    Group('online-users').send({
        'text': json.dumps(data)
    })


@channel_session_user
def location_send(message):
    detlog(message)


@channel_session_user
def location_disconnect(message):
    message.channel_session.flush()
    # FIXME With a new commit, the line below is no longer needed to ensure
    # session deletion. Remove it after testing that session gets deleted upon
    # removing the line.
    message.channel_session.modified = False
    user_id = message.channel_session.get('__auth_user_id')
    delete_session(user_id)
    Group('online-users').discard(message.reply_channel)


def delete_session(user_id):
    for session in Session.objects.all():
        if session.get_decoded().get('__auth_user_id') == user_id:
            session.delete()


