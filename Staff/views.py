from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import face_recognition
import numpy as np
from .utils import detect_eyes, get_ip_location
from .models import Log

# Create your views here.
@csrf_exempt
def auth_logout(request):
    Token.objects.get(user=request.user).delete()
    Log.objects.create(user=request.user, action="Logout")
    logout(request)
    return HttpResponse(status=200)

@csrf_exempt
def login(request):
    # print(request.META)
    ipInfo = get_ip_location(request)
    return HttpResponse(status=401)

@csrf_exempt
def login2(request):
    username = request.POST['username']
    password = request.POST['password']
    faceImage = request.FILES.get('image')
    user = authenticate(username=username, password=password)

    if user:
        if faceImage:
            image = face_recognition.load_image_file(faceImage)
            face_encodings = face_recognition.face_encodings(image)

            # Ensure that only one face is detected
            if len(face_encodings) == 1:
                user_face_encodings = user.deserialize_face_encodings()
                user_face_encodings = np.array(user_face_encodings)
                if not detect_eyes(image):
                    Log.objects.create(user=user, action="Login Failed - Eyes are not open.")
                    return JsonResponse({"message": "Eyes are not open"}, status=405)
                #check if user face correctly matches
                results = face_recognition.compare_faces([user_face_encodings],face_encodings[0],tolerance=0.6)
                if results[0]:
                    #delete any previous token
                    prevToken=Token.objects.filter(user=user)
                    if len(prevToken)>0:
                        prevToken.delete()
                    #create and save token
                    newToken=Token(user=user)
                    newToken.save()
                    ipInfo = get_ip_location(request)
                    Log.objects.create(user=user, action="Login Successful", description=f"User IP Info: {ipInfo}")
                    return JsonResponse({
                        "token":newToken.key
                    })
                else:
                    Log.objects.create(user=user, action="Login Failed - Face does not match.")
                    return JsonResponse(
                    {"message": "Face does not match."},
                    status=409
                )
            else:
                # Reject the image if more or fewer than one face is detected
                Log.objects.create(user=user, action="Login Failed - Invalid number of faces detected.")
                return JsonResponse(
                    {"message": "Invalid number of faces detected. Please capture an image with exactly one face."},
                    status=408
                )
    return HttpResponse(status=401)

@csrf_exempt
def checkToken(request):
    token = request.POST['token']
    try:
        token_obj = Token.objects.get(key=token)
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=401)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        faceImage = request.FILES.get('image')

        try:
            # Check for empty fields
            if not (username and name and email and password and faceImage):
                return JsonResponse({"message": "All fields are required"}, status=400)

            # Check if the username is already taken
            User = get_user_model()
            if User.objects.filter(username=username).exists():
                return JsonResponse({"message": "Username already exists"}, status=409)

            if faceImage:
                image = face_recognition.load_image_file(faceImage)
                face_encodings = face_recognition.face_encodings(image)

                # Ensure that only one face is detected
                if len(face_encodings) == 1:
                    if not detect_eyes(image):
                        return JsonResponse({"message": "Eyes are not open"}, status=405)
                    # Create User
                    user = User.objects.create_user(
                        username=username,
                        name=name,
                        email=email,
                        password=password,
                        face_encodings=list(face_encodings[0])
                    )
                    #Log
                    Log.objects.create(user=user, action="User account created")
                    return JsonResponse({"message": "Registration successful"}, status=200)
                else:
                    # Reject the image if more or fewer than one face is detected
                    return JsonResponse(
                        {"message": "Invalid number of faces detected. Please capture an image with exactly one face."},
                        status=408
                    )
            else:
                return JsonResponse({"message": "No image provided"}, status=408)

        except Exception as e:
            return JsonResponse({"message": "Unexpected error"}, status=500)

    return HttpResponse(status=401)

@csrf_exempt
def register2(request):
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

            return JsonResponse({"message": "Registration successful"}, status=200)
        except Exception as e:
            return JsonResponse({"message": "Unexpected error"}, status=500)

    return HttpResponse(status=401)