from channels.auth import channel_session_user_from_http, channel_session_user
from channels import Group
from FriendTrackerApp.models import Location, Follow, CustomSession
from FriendTrackerApp.views import reply_channels
from FriendTrackerApp.globals import all_raw_locations, all_processed_locations
import queue
from .detlogging import detlog
import json
import threading


@channel_session_user_from_http
def location_connect(message):
    if location_connect.first_user:
        location_connect.first_user = False
        thread = threading.Thread(target=process_locations)
        thread.start()
    message.http_session.flush()
    message.http_session.modified = False
    reply_channels[message.user.id] = message.reply_channel
    Group('online-users').add(message.reply_channel)

    user_raw_locations = queue.Queue()
    user_raw_locations.alive = True

    user_processed_locations = queue.Queue()
    user_processed_locations.alive = True

    all_raw_locations[message.user.id] = user_raw_locations
    all_processed_locations[message.user.id] = user_processed_locations

    data = {'sessionid': message.channel_session.session_key}
    message.reply_channel.send({
        'accept': True,
        'text': json.dumps(data)
    })

location_connect.first_user = True


class Location:
    def __init__(self, timestamp, latitude, longitude):
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude


@channel_session_user
def location_receive(message):
    data = json.loads(message.content['text'])
    data['user'] = message.user.id
    #print(data)
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
        location = Location(data['timestamp'], data['latitude'], data['longitude'])
        all_raw_locations[message.user.id].put(location)


to_process_count = 5

def process_locations():
    while True:
        for user_id, user_locations in list(all_raw_locations.items()):
            count = to_process_count
            while count != 0:
                try:
                    location = user_locations.get(block=False)
                except queue.Empty:
                    if not user_locations.alive:
                        del all_raw_locations[user_id]
                    break
                count -= 1
                if count == to_process_count - 1:
                    timestamp = location.timestamp
                    latitude = location.latitude
                    longitude = location.longitude
                else:
                    if count == 0:
                        processed_location = Location(timestamp / to_process_count
                                , latitude / to_process_count
                                , longitude / to_process_count)
                        all_processed_locations[user_id].put(processed_location)
                    else:
                        timestamp += location.timestamp
                        latitude += location.latitude
                        longitude += location.longitude
                user_locations.task_done()


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
    all_raw_locations[message.user.id].alive = False
    all_processed_locations[message.user.id].alive = False
    Group('online-users').discard(message.reply_channel)

