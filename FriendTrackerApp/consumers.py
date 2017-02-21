from channels.auth import channel_session_user_from_http, channel_session_user
from channels import Group
from FriendTrackerApp.models import Location, Follow, CustomSession
from FriendTrackerApp.views import reply_channels
from .detlogging import detlog
import json


@channel_session_user_from_http
def location_connect(message):
    message.http_session.flush()
    message.http_session.modified = False
    reply_channels[message.user.id] = message.reply_channel
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
    accuracy = data['accuracy']
    # We don't check if accuracy is less than 0, because this check is already
    # being done at the client. I choose not to do this check on the server,
    # because this method is the busiest method of the application.
    #
    # if accuracy >= 0 && accuracy <= 5:
    #
    # FIXME Don't use a "magic number". Put the 5 (or another number) to a
    # constant (or variable, or enum, etc.) and use this constant.
    if accuracy <= 10:
        location_receive.counter -= 1
        if location_receive.counter == average_count_number - 1:
            location_receive.latitude = data['latitude']
            location_receive.longitude = data['longitude']
        else:
            location_receive.latitude += data['latitude']
            location_receive.longitude += data['longitude']
            if location_receive.counter == 0:
                data['latitude'] = location_receive.latitude / average_count_number
                data['longitude'] = location_receive.longitude / average_count_number
                Group('online-users').send({
                    'text': json.dumps(data)
                })
                location_receive.counter = average_count_number


average_count_number = 5
location_receive.counter = average_count_number
location_receive.latitude = 0
location_receive.longitude = 0


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
    del reply_channels[message.user.id]
    Group('online-users').discard(message.reply_channel)

