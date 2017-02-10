from channels.auth import channel_session_user_from_http, channel_session_user
from channels import Group
from FriendTrackerApp.models import Location, Follower, CustomSession
from FriendTrackerApp.views import reply_channels
from .detlogging import detlog
import json


@channel_session_user_from_http
def location_connect(message):
    message.http_session.flush()
    message.http_session.modified = False
    reply_channels[message.user.username] = message.reply_channel
    Group('online-users').add(message.reply_channel)
    data = {'sessionid': message.channel_session.session_key}
    message.reply_channel.send({
        'accept': True,
        'text': json.dumps(data)
    })


@channel_session_user
def location_receive(message):
    data = json.loads(message.content['text'])
    data['user'] = message.user.id
    print(data)
    data['command'] = 'location'
    Group('online-users').send({
        'text': json.dumps(data)
    })


@channel_session_user
def location_send(message):
    detlog(message)


@channel_session_user
def location_disconnect(message):
    # FIXME With a new commit to Django Channels, the
    #     message.channel_session.modified = False
    # line is no longer needed to ensure session deletion. Remove it after
    # testing that session gets deleted upon removing the line.
    # NOTE You might want to use Django's logout function, since Django's
    # logout function signals that the user has logged out. You might need
    # this functionality if other users need to know if a particular user has
    # logged out (that is, disconnected).
    message.channel_session.flush()
    message.channel_session.modified = False
    del reply_channels[message.user.username]
    Group('online-users').discard(message.reply_channel)

