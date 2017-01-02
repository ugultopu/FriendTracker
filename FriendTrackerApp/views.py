from django.shortcuts import render
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
#from .detlogging import detlog


@csrf_exempt
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        return HttpResponse(json.dumps({'status': 0,
                                        'sessionid': request.session.session_key}))
    return HttpResponse(json.dumps({'status': 1}))

