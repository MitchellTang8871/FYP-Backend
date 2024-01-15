from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model

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

@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            # Check if the username is already taken
            User = get_user_model()
            if User.objects.filter(username=username).exists():
                response = {"message": "Username already exists"}
                return JsonResponse({"message": "Username already exists"}, status=409)

            # Create a new user
            user = User.objects.create_user(username=username, name=name, email=email, password=password)

            # return JsonResponse({"message": "Registration successful"}, status=200)
        except Exception as e:
            return JsonResponse({"message": "Unexpected error"}, status=500)

    return HttpResponse(status=401)