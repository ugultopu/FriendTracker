from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from .detlogging import detlog


@csrf_exempt
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        try:
            auth.login(request, user)
            detlog(request.session)
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
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            try:
                auth.login(request, user)
                detlog(request.session)
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
    except:
        return HttpResponse(json.dumps({'status': 'Unknown error'}))



