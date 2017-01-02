from channels.auth import channel_session_user_from_http, channel_session_user
from channels import Group


@channel_session_user_from_http
def location_connect(message):
    Group('online-users').add(message.reply_channel)


@channel_session_user
def location_receive(message):



@channel_session_user
def location_send(message):



@channel_session_user
def location_disconnect(message):
    Group('online-users').discard(message.reply_channel)



