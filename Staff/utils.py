import cv2
import numpy as np
import requests
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
    lower_white = np.array([0, 0, 100])
    upper_white = np.array([179, 30, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    print("White pixels:", cv2.countNonZero(mask))
    print("HSV Values:", hsv)
    if cv2.countNonZero(mask) > 0:
        return True
    return False

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
        print(ip)
    else:
        ip = request.META.get('REMOTE_ADDR')
        print("remote_addr: ", ip)
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