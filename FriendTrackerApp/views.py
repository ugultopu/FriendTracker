from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from FriendTrackerApp.models import Follower, PinnedLocation
from django.core import serializers
import uuid
import json
from .detlogging import detlog
import traceback

reply_channels = {}
follows = {}
follow_requests = {}

@csrf_exempt
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        try:
            auth.login(request, user)
            session_key = request.session.session_key
            if session_key is not None:
                return HttpResponse(json.dumps({'status': 'Success',
                    'sessionid': session_key}))
            else:
                return HttpResponse(json.dumps({'status': 'Empty session key'}))
        except Exception as e:
            detlog(e)
            return HttpResponse(json.dumps({'status': 'Cannot log in'}))
    else:
        return HttpResponse(json.dumps({'status': 'Cannot authenticate'}))


@csrf_exempt
def register(request):
    firstname = request.POST['firstname']
    lastname = request.POST['lastname']
    email = request.POST['email']
    # TODO: Extend the User model to add a Phone Number field to it. Then,
    # save the phonenumber to the model.
    phonenumber = request.POST['phonenumber']
    username = request.POST['username']
    password = request.POST['password']

    # TODO: Determine the cause of the exception and either handle it, or return a
    # suitable status code.
    try:
        user = User.objects.create_user(username, email, password,
                first_name=firstname, last_name=lastname)
        user.save()
        return HttpResponse(json.dumps({'status': 'Success'}))
    except:
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'status': 'Cannot create user'}))


@csrf_exempt
def follow_request(request):
    followee_username = request.user.username
    try:
        follower_username = request.POST['username']
        follower = User.objects.get(username=follower_username)
    except:
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'status': 'Follower not found'}))

    # TODO Decide if it should be possible to follow yourself
    # if follower_username == followee_username:
    #     return HttpResponse(json.dumps({'status': 'Success'}))

    try:
        follower_reply_channel = reply_channels[follower_username]
    except:
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'status': 'Follower offline'}))
    try:
        token = str(uuid.uuid4())
        follow_requests[token] = {
                'followee_username': followee_username,
                'follower_username': follower_username
                }
        data = {
                'command': 'follow_request',
                'followee_username': followee_username,
                'token': token
                }
        follower_reply_channel.send({
            'text': json.dumps(data)
            })
    except:
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'status': 'Cannot send follow request'}))
    return HttpResponse(json.dumps({'status': 'Success'}))


@csrf_exempt
def follow_response(request):
    follower_username = request.user.username
    try:
        request_body = json.loads(request.body)
    except:
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'status': 'Invalid JSON'}))
    token = request_body['token']
    response = request_body['response']
    try:
        follow_request = follow_requests[token]
    except:
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'status': 'Non-existent follow request'}))
    # TODO Determine if it is necessary to check for follower username at the
    # follow request
    if follow_request['follower_username'] != follower_username:
        return HttpResponse(json.dumps({'status': 'Follower names do not match'}))
    followee_username = follow_request['followee_username']
    if response == 'Follow':
        try:
            follows[follower_username].append(followee_username)
        except:
            follows[follower_username] = [followee_username]
            # follows[follower_username].append(followee_username)
        data = {'response': 'Follow'}
    elif response == 'No follow':
        data = {'response': 'No follow'}
    else:
        return HttpResponse(json.dumps({'status': 'Unknown follow response'}))
    data['command'] = 'follow_response'
    data['follower_username'] = follower_username
    reply_channels[followee_username].send({
        'text': json.dumps(data)
        })
    del follow_requests[token]
    return HttpResponse(json.dumps({'status': 'Success'}))


@csrf_exempt
def location_operations(request):
    try:
        request_body = json.loads(request.body)
    except:
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'status': 'Invalid JSON'}))
    try:
        command = request_body['command']
    except:
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'status': 'No command specified'}))
    if command == 'save':
        # Save a location to data base.
        try:
            name = request_body['name']
            latitude = request_body['latitude']
            longitude = request_body['longitude']
        except:
            print(traceback.format_exc())
            return HttpResponse(json.dumps({'status': 'Bad command parameters'}))
        try:
            PinnedLocation.objects.create(user=request.user, name=name, latitude=latitude, longitude=longitude)
        except:
            print(traceback.format_exc())
            return HttpResponse(json.dumps({'status': 'Cannot save location'}))
        return HttpResponse(json.dumps({'status': 'Success'}))
    elif command == 'load':
        # Get all saved locations
        try:
            pinned_locations = PinnedLocation.objects.filter(user=request.user)
        except:
            print(traceback.format_exc())
            return HttpResponse(json.dumps({'status': 'Cannot get locations'}))
        # FIXME The default serializer includes a lot of unnecessary
        # information as well in the sent JSON. Maybe I will manually serialize
        # the pinned locations to a JSON.
        return HttpResponse(json.dumps({'status': 'Success',
                                        'locations': serializers.serialize('json', pinned_locations)}))
    else:
        return HttpResponse(json.dumps({'status': 'Unrecognized command'}))


