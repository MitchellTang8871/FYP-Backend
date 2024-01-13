from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
@csrf_exempt
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    if user:
        #delete any previous token
        prevToken=Token.objects.filter(user=user)
        if len(prevToken)>0:
            prevToken.delete()
        #create and save token
        newToken=Token(user=user)
        newToken.save()
        return JsonResponse({
            "token":newToken.key
        })
    return HttpResponse(status=401)