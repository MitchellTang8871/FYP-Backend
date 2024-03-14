from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from . import serializers
from django.contrib.auth import get_user_model
import face_recognition
import numpy as np
from .utils import getRequester, detect_eyes, get_ip_location, create_token, generate_and_send_otp, verify_otp, create_usual_login_location, draw_faces, get_main_face_encoding, draw_main_face
from .models import Log, UsualLoginLocation, User, Transactions, allowTransactionIp
from django.conf import settings
import os
from datetime import datetime
from django.core.files.storage import FileSystemStorage
import cv2
from PIL import Image, ImageDraw
import io
import base64
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q
from decimal import Decimal
import re
from django.core.files.base import ContentFile

#ASC
from django.db import connection

# Create your views here.
@csrf_exempt
def logout(request):
    http_auth_token = request.META.get('HTTP_AUTHORIZATION')

    if http_auth_token and http_auth_token != "undefined":
        theToken = http_auth_token.split(" ")[1]

        try:
            token = Token.objects.get(key=theToken)
            theUser = token.user
        except ObjectDoesNotExist:
            # Invalid token
            return HttpResponse(status=460)

        # Token retrieval successful, delete token and create log
        token.delete()
        Log.objects.create(user=theUser, action="Logout")
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=460)  # Bad request, token not provided

@csrf_exempt
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    faceImage = request.FILES.get('image')
    otp = request.POST.get('otp')
    user = authenticate(username=username, password=password)
    if user:
        if faceImage:
            image = face_recognition.load_image_file(faceImage)

            #development checking only ## face detected
            # face_locations = face_recognition.face_locations(image)
            # if len(face_locations) > 0:
            #     draw_faces(faceImage, face_locations)

            #get main face endcoding
            main_face_encoding = get_main_face_encoding(image)
            if main_face_encoding is None:
                return JsonResponse({"message": "No face detected"}, status=408)
            # face_encodings = face_recognition.face_encodings(image)
            face_encodings = main_face_encoding
            # print(face_encodings)

            # Ensure that only one face is detected
            if len(face_encodings) == 1:
                user_face_encodings = user.deserialize_face_encodings()
                user_face_encodings = np.array(user_face_encodings)
                if not detect_eyes(image):
                    # Log.objects.create(user=user, action="Login Failed - Eyes are not open.")
                    return JsonResponse({"message": "Eyes are not open, might be lighting issue"}, status=405)
                #check if user face correctly matches
                results = face_recognition.compare_faces([user_face_encodings],face_encodings[0],tolerance=0.6)
                if results[0]: #if user face matches
                    ipInfo = get_ip_location(request)

                    #check account activation
                    if not user.emailVerified:
                        if otp is None or len(str(otp).strip()) == 0:
                            if generate_and_send_otp(user, "Account Activation"):
                                Log.objects.create(user=user, action="OTP Sent, Account Activation", description=user.email)
                                return JsonResponse({"message": "Account Inactive, Please get OTP from email."}, status=406)
                            else:
                                return JsonResponse({"message": "Unexpected error while sending OTP"}, status=406)
                        else:
                            if verify_otp(otp, user):
                                user.emailVerified = True
                                user.save()
                                Log.objects.create(user=user, action="OTP Verified, Account Activated")
                                create_usual_login_location(user, ipInfo)
                                Log.objects.create(user=user, action="OTP Verified, New Login Location Recorded", description=f"User IP Info: {ipInfo}")
                                token = create_token(request, user)
                                Log.objects.create(user=user, action="Login Successful", description=f"User IP Info: {ipInfo}")
                                return JsonResponse({"token":token}, status=200)
                            else:
                                Log.objects.create(user=user, action="OTP Verification Failed, Failed to Activate Account", description=f"User IP Info: {ipInfo}")
                                return JsonResponse({"message": "OTP Verification Failed, Invalid OTP"}, status=406)

                    #check for usual location
                    usual_login_locations = UsualLoginLocation.objects.filter(user=user)
                    # if ipInfo.get("status") == "success" and ipInfo.get("query") in usual_login_locations.values_list('userIp', flat=True): #login from usual location
                    if ipInfo.get("query") in usual_login_locations.values_list('userIp', flat=True): #local development environment purpose
                        token = create_token(request, user)
                        Log.objects.create(user=user, action="Login Successful", description=f"User IP Info: {ipInfo}")
                        return JsonResponse({"token":token}, status=200)
                    # elif ipInfo.get("status") == "success":
                    elif ipInfo.get("status") == "success" or ipInfo.get("status") == "fail" and ipInfo.get("query") == "127.0.0.1": #local development environment purpose
                        if otp is None or len(str(otp).strip()) == 0:
                            if generate_and_send_otp(user, "Login"):
                                Log.objects.create(user=user, action="OTP Sent, New Login Location Detected", description=f"User IP Info: {ipInfo}, {user.email}")
                                return JsonResponse({"message": "New Login Location Detected, please get OTP from email"}, status=406)
                            else:
                                return JsonResponse({"message": "Unexpected error while sending OTP"}, status=406)
                        else:
                            if verify_otp(otp, user):
                                create_usual_login_location(user, ipInfo)
                                Log.objects.create(user=user, action="OTP Verified, New Login Location Recorded", description=f"User IP Info: {ipInfo}")
                                token = create_token(request, user)
                                Log.objects.create(user=user, action="Login Successful", description=f"User IP Info: {ipInfo}")
                                return JsonResponse({"token":token}, status=200)
                            else:
                                Log.objects.create(user=user, action="OTP Verification Failed, New Login Location Detected", description=f"User IP Info: {ipInfo}")
                                return JsonResponse({"message": "OTP Verification Failed, Invalid OTP"}, status=406)
                    else:
                        return JsonResponse({"message": "Unexpected ip address detection error"}, status=500)
                else:
                    #highlight main face
                    image_with_highlighted_face = draw_main_face(faceImage)
                    # Generate a unique filename using username and current datetime
                    currentDatetime = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
                    filename = f"{username}-{currentDatetime}.jpg"
                    # Save the image
                    fs = FileSystemStorage()
                    # Wrap the bytes data in a ContentFile
                    file_to_save = ContentFile(image_with_highlighted_face)
                    filename = fs.save(filename, file_to_save)
                    uploaded_file_path = fs.path(filename)
                    Log.objects.create(user=user, action="Login Failed - Face does not match.", description=uploaded_file_path)
                    return JsonResponse(
                        {"message": "Face does not match."},
                        status=409
                    )
            else:
                # Reject the image if more or fewer than one face is detected
                Log.objects.create(user=user, action="Login Failed - Invalid number of faces detected.")
                return JsonResponse(
                    {"message": "Invalid number of faces detected. Please scan with exactly one face."},
                    status=408
                )
        else:
            return JsonResponse({"message": "No face detected"}, status=408)
    return JsonResponse({"message": "Invalid credentials"}, status=401)

@csrf_exempt
def checkToken(request):
    token = request.POST['token']
    try:
        token_obj = Token.objects.get(key=token)
        return HttpResponse(status=200)
    except ObjectDoesNotExist:
        return JsonResponse({"message": "Invaild Token"}, status=460)

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

            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({"message": "Invalid email format"}, status=400)

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
                    return JsonResponse({"message": "Registration successful, Please login to activate your account"}, status=200)
                else:
                    # Reject the image if more or fewer than one face is detected
                    face_locations = face_recognition.face_locations(image)
                    encodedImage = None
                    if len(face_locations) > 0:
                        #  Draw bounding box around the face
                        image = Image.open(faceImage)
                        draw = ImageDraw.Draw(image)
                        for (top, right, bottom, left) in face_locations:
                            draw.rectangle(((left, top), (right, bottom)), outline=(255, 0, 0), width=2)

                        with io.BytesIO() as output:
                            image.save(output, format='JPEG')
                            encodedImage = base64.b64encode(output.getvalue()).decode()

                    # Send the modified image and message as response
                    return JsonResponse({
                        "message": "Invalid number of faces detected. Please capture an image with exactly one face.",
                        "encodedImage": encodedImage
                    }, status=408)
            else:
                return JsonResponse({"message": "No image provided"}, status=408)

        except Exception as e:
            error_message = str(e)  # Convert the exception to a string
            return JsonResponse({"message": "Unexpected error"}, status=500)

    return HttpResponse(status=401)

@csrf_exempt
def resendOtp(request):
    action = request.POST.get('action')
    theUser = getRequester(request)

    if action is None:
        action = "Resend OTP"
    if theUser is not None:
        generate_and_send_otp(theUser, action)
        Log.objects.create(user=theUser, action=f"OTP Sent, {action}", description=theUser.email)
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            generate_and_send_otp(user, action)
            Log.objects.create(user=user, action=f"OTP Sent, {action}", description=user.email)
        else:
            return HttpResponse(status=401)
    return HttpResponse(status=200)

@csrf_exempt
def getActivityLogs(request):
    theUser = getRequester(request)
    logs = Log.objects.filter(user=theUser).order_by('-timestamp')
    serialized_logs = serializers.ActivityLogsSerializer(logs, many=True).data
    return JsonResponse(serialized_logs, safe=False)

@csrf_exempt
def getResults(request):
    otp = request.POST.get('otp')

    theUser = getRequester(request)
    if otp:
        if verify_otp(otp, theUser):
            data = {
                'name': theUser.name,
                'username': theUser.username
            }
            result = BytesIO()
            template = get_template("result.html")
            html = template.render(data)
            pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), dest=result)
            if not pdf.err:
                return HttpResponse(result.getvalue(), content_type='application/pdf')
            else:
                return HttpResponse(status=500)
        else:
            Log.objects.create(user=theUser, action="OTP Verification Failed, Failed to Check Exam Result")
            return JsonResponse({"message": "OTP Verification Failed, Invalid OTP"}, status=406)
    else:
        return JsonResponse({"message": "OTP Verification Failed, Invalid OTP"}, status=406)

@csrf_exempt
def getUserCredit(request):
    theUser = getRequester(request)
    if theUser:
        return JsonResponse({"credit": theUser.myr})
    else:
        return JsonResponse({"message": "user not found"}, status=406)

@csrf_exempt
def searchUsers(request):
    searchTerm = request.POST.get('searchTerm')
    theUser = getRequester(request)
    if searchTerm:
        users = User.objects.filter(name__startswith=searchTerm).exclude(username=theUser.username).order_by('-date_joined')
        serialized_users = serializers.SimpleUserSerializer(users, many=True).data


        return JsonResponse(serialized_users, safe=False)
    else:
        return JsonResponse({"message": "Please Enter Search Term"}, status=406)

#Advance Software Security
@csrf_exempt
def searchUsers2(request):
    print("RUN")
    searchTerm = request.POST.get('searchTerm')
    theUser = getRequester(request)
    if searchTerm:
        # Crafted to be vulnerable to SQL injection
        # '; DELETE FROM Staff_log
        query = "SELECT * FROM Staff_user WHERE name LIKE '%s' ORDER BY date_joined DESC;" % searchTerm
        with connection.cursor() as cursor:
            cursor.executescript(f"SELECT * FROM Staff_user WHERE name LIKE '%{searchTerm}%' ORDER BY date_joined DESC;")
            rows = cursor.fetchall()
        serialized_users = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

        return JsonResponse(serialized_users, safe=False)
    else:
        return JsonResponse({"message": "Please Enter Search Term"}, status=406)


@csrf_exempt
def pay(request):
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        faceImage = request.FILES.get('image')
        theUser = getRequester(request)
        if faceImage:
            image = face_recognition.load_image_file(faceImage)

            #get main face endcoding
            main_face_encoding = get_main_face_encoding(image)
            if main_face_encoding is None:
                return JsonResponse({"message": "No face detected"}, status=408)
            face_encodings = main_face_encoding

            # Ensure that only one face is detected
            if len(face_encodings) == 1:
                user_face_encodings = theUser.deserialize_face_encodings()
                user_face_encodings = np.array(user_face_encodings)
                if not detect_eyes(image):
                    return JsonResponse({"message": "Eyes are not open, might be lighting issue"}, status=405)
                #check if user face correctly matches
                results = face_recognition.compare_faces([user_face_encodings],face_encodings[0],tolerance=0.6)
                if results[0]: #if user face matches
                    #check is ip authenticated
                    ipInfo = get_ip_location(request)
                    allowedIps = allowTransactionIp.objects.all()
                    # if ipInfo.get("status") == "success" and ipInfo.get("query") in usual_login_locations.values_list('userIp', flat=True): #login from usual location
                    if ipInfo.get("query") in allowedIps.values_list('ip', flat=True): #local development environment purpose
                        if receiver_username and amount and description:
                            try:
                                theReceiver = User.objects.get(username=receiver_username)
                            except ObjectDoesNotExist:
                                return JsonResponse({"message": "Receiver not found"}, status=404)

                            amount_pattern = re.compile(r'^\d+(\.\d{1,2})?$')
                            if not amount_pattern.match(amount):
                                return JsonResponse({"message": "Invalid amount format"}, status=400)

                            amount = Decimal(amount)
                            if amount <= 0:
                                return JsonResponse({"message": "Amount must be greater than zero"}, status=400)

                            theUser = getRequester(request)
                            if theUser.myr < amount:
                                return JsonResponse({"message": "Insufficient funds"}, status=400)

                            theUser.myr -= amount
                            theReceiver.myr += amount

                            transaction = Transactions.objects.create(user=theUser, receiver=theReceiver, amount=amount, description=description)
                            transaction.save()
                            theUser.save()
                            theReceiver.save()

                            return JsonResponse({"message": "Payment Successful"}, status=200)
                        else:
                            return JsonResponse({"message": "Please provide receiver, amount, and description"}, status=400)
                    else:
                        Log.objects.create(user=theUser, action="Transaction Failed - IP not allowed for transaction.", description=f"IP Info: {ipInfo}")
                        return JsonResponse({"message": "Your current connection is not allowed to make transaction"}, status=409)
                else:
                    #highlight main face
                    image_with_highlighted_face = draw_main_face(faceImage)
                    # Generate a unique filename using username and current datetime
                    currentDatetime = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
                    filename = f"{theUser.username}-{currentDatetime}.jpg"
                    # Save the image
                    fs = FileSystemStorage()
                    # Wrap the bytes data in a ContentFile
                    file_to_save = ContentFile(image_with_highlighted_face)
                    filename = fs.save(filename, file_to_save)
                    uploaded_file_path = fs.path(filename)
                    Log.objects.create(user=theUser, action="Transaction Failed - Face does not match.", description=uploaded_file_path)
                    return JsonResponse(
                        {"message": "Face does not match."},
                        status=409
                    )
        else:
            return JsonResponse({"message": "No face detected"}, status=408)
    else:
        return JsonResponse({"message": "Method not allowed"}, status=405)

@csrf_exempt
def getTransactions(request):
    theUser = getRequester(request)
    transactions = Transactions.objects.filter(Q(user=theUser) | Q(receiver=theUser)).order_by('-timestamp')

    # Create a list to store modified transactions for front-end use
    modified_transactions = []

    for transaction in transactions:
        data = serializers.TransactionsSerializer(transaction).data
        if transaction.user == theUser:
            # Convert amount to decimal and negate it
            data['amount'] = -Decimal(data['amount'])
        modified_transactions.append(data)

    return JsonResponse(modified_transactions, safe=False)












