from channels.auth import channel_session_user_from_http, channel_session_user
from channels import Group
from .detlogging import detlog


@channel_session_user_from_http
def location_connect(message):
    detlog(message)
    Group('online-users').add(message.reply_channel)


@channel_session_user
def location_receive(message):
    print('dummy')


@channel_session_user
def location_send(message):
    print('dummy')


@channel_session_user
def location_disconnect(message):
    Group('online-users').discard(message.reply_channel)


