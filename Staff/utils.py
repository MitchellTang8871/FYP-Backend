import cv2
import numpy as np
import requests
from rest_framework.authtoken.models import Token
import random
import string
from django.core.mail import EmailMessage
from .models import Otp, UsualLoginLocation
from datetime import datetime, timedelta
from django.utils import timezone


def detect_eyes(face_image):
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
    eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)

    for (ex, ey, ew, eh) in eyes:
        if ew > 15 and eh > 15:  # Check if the eye is large enough
            center = (ex + ew // 2, ey + eh // 2)
            radius = int(ew * 0.5)
            if is_eye_open(face_image, center, radius):
                return True

    return False

def is_eye_open(face_image, center, radius):
    x, y = center
    r = radius
    eye_region = face_image[y-r:y+r, x-r:x+r]
    hsv = cv2.cvtColor(eye_region, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 80])
    upper_white = np.array([179, 30, 255])
    # lower_white = np.array([100, 0, 100])
    # upper_white = np.array([130, 30, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    # print("White pixels:", cv2.countNonZero(mask))
    # print("HSV Values:", hsv)
    # print("Eye Region Shape:", eye_region.shape)
    # cv2.imshow("Eye Region", eye_region)
    # cv2.imshow("HSV Mask", mask)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    if cv2.countNonZero(mask) > 0:
        return True
    return False

def get_client_ip(request):
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        # print("x_real_ip: ", x_real_ip)
        return x_real_ip
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # print("x_forwarded_for: ", x_forwarded_for)
            ip = x_forwarded_for.split(',')[0]
            return ip
        else:
            ip = request.META.get('REMOTE_ADDR')
            # print("REMOTE_ADDR: ", ip)
            return ip


def get_ip_location(request):
    try:
        # userIp = requests.get("http://api.ipify.org").text
        userIp = get_client_ip(request)
        ipInfo = requests.get(f"http://ip-api.com/json/{userIp}").json()
        print(ipInfo)
        return ipInfo
    except Exception as e:
        print(e)
        return None

def create_token(request, user):
    #delete any previous token
    prevToken=Token.objects.filter(user=user)
    if len(prevToken)>0:
        prevToken.delete()
    #create and save token
    newToken=Token(user=user)
    newToken.save()
    return newToken.key

def generate_and_send_otp(user, action):
    try:
        prevOtp=Otp.objects.filter(user=user)
        if len(prevOtp)>0:
            prevOtp.delete()
        otp = ''.join(random.choices(string.digits, k=6))
        Otp.objects.create(
            user=user,
            otp=otp,
            validUntil=timezone.now() + timezone.timedelta(minutes=5) # 5 minutes validity
        )
        subject = f'Your OTP for {action}'
        message = f'Your OTP is: {otp}. Please use this OTP to verify your action: {action}.'
        email = EmailMessage(subject, message, to=[user.email])
        if email.send():
            return True
    except Exception as e:
        return False

def verify_otp(otp, user):
    print("verifiing otp: ",otp)
    try:
        otpObj = Otp.objects.get(user=user, otp=otp, validUntil__gte=timezone.now())
        otpObj.delete()
        return True
    except Exception as e:
        print(e)
        return False

def create_usual_login_location(user, ipInfo):
    # Get the number of existing usual login locations for the user
    num_locations = UsualLoginLocation.objects.filter(user=user).count()

    # If there are already 3 locations, delete the oldest one
    if num_locations >= 3:
        oldest_location = UsualLoginLocation.objects.filter(user=user).order_by('timestamp').first()
        if oldest_location:
            oldest_location.delete()

    # Create a new usual login location
    UsualLoginLocation.objects.create(
        user=user,
        userIp=ipInfo.get("query"),
        city=ipInfo.get("city"),
        country=ipInfo.get("country"),
        details=ipInfo
    )
    return