from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from FriendTrackerApp.models import User, Follow, FollowRequest, PinnedLocation
from django.core import serializers
import uuid
import json
from .detlogging import detlog
import traceback

# FIXME Decide where to put the following.
#
# It cannot be put into a database table, because a Berkeley Socket (that is,
# the Python implementation of a Berkeley Socket) cannot be serialized. This is
# by definition of Python Sockets. That is, a Python socket has a built in
# exception which is thrown when it is tried to be serialized.
#
# Maybe putting it into Redis is a good option.
reply_channels = {}

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
            print(traceback.format_exc())
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
@login_required
def follow_request(request):
    followee = User.objects.get(username=request.user.username)
    try:
        follower = User.objects.get(username=request.POST['username'])
    except:
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'status': 'Follower not found'}))

    try:
        follower_reply_channel = reply_channels[follower.id]
    except:
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'status': 'Follower offline'}))

    # TODO Decide if it should be possible to follow yourself
    # if follower_username == followee_username:
    #     return HttpResponse(json.dumps({'status': 'Success'}))

    try:
        FollowRequest.objects.get(follower=follower, followee=followee)
        return HttpResponse(json.dumps({'status': 'Follow request exists'}))
    except:
        pass

    try:
        Follow.objects.get(follower=follower, followee=followee)
        return HttpResponse(json.dumps({'status': 'Follower already follows'}))
    except:
        pass

    try:
        token = str(uuid.uuid4())
        FollowRequest(token=token, followee=followee, follower=follower).save()
        data = {
                'command': 'follow_request',
                'followee_username': request.user.username,
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
@login_required
def follow_response(request):
    follower = request.user

    try:
        request_body = json.loads(request.body)
    except:
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'status': 'Invalid JSON'}))

    token = request_body['token']
    response = request_body['response']

    # TODO Determine if it is necessary to check for follower username at the
    # follow request
    try:
        follow_request = FollowRequest.objects.get(token=token, follower=follower)
    except:
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'status': 'Non-existent follow request'}))

    followee = follow_request.followee

    if response == 'Follow':
        try:
            Follow(follower=follower, followee=followee).save()
        except:
            print(traceback.format_exc())
            return HttpResponse(json.dumps({'status': 'Cannot save follow request'}))
        data = {'response': 'Follow'}
    elif response == 'No follow':
        data = {'response': 'No follow'}
    else:
        return HttpResponse(json.dumps({'status': 'Unknown follow response'}))

    data['command'] = 'follow_response'
    data['follower_username'] = follower.username
    reply_channels[follower.id].send({
        'text': json.dumps(data)
        })
    follow_request.delete()
    return HttpResponse(json.dumps({'status': 'Success'}))


@csrf_exempt
@login_required
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


