import re
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import json
from django.utils import timezone


# Create your models here.
class User(AbstractUser):
    USERNAME_FIELD = "username"

    username = models.CharField(max_length=24, unique=True)
    name = models.CharField(default="Anonymous", max_length=120)
    email = models.EmailField(default=None, max_length=100, null=True, blank=True)
    emailVerified = models.BooleanField(default=False)
    face_encodings = models.TextField(null=True, blank=True)
    myr = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if self.name is not None:
            self.name = re.sub(r" +", " ", self.name).strip()

        if self.name == "":
            self.name = None

        if self.email == "":
            self.email = None

        # Serialize face_encodings to JSON before saving
        if isinstance(self.face_encodings, list):
            self.face_encodings = json.dumps(self.face_encodings)

        super(User, self).save(*args, **kwargs)

    def deserialize_face_encodings(self):
        # Deserialize face_encodings from JSON
        if self.face_encodings:
            return json.loads(self.face_encodings)
        return None

class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.TextField()
    description = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"

class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="receiver")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class UsualLoginLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    userIp = models.CharField(max_length=255)
    city = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save_details(self, details):
        # Convert the dictionary to a JSON string
        details_json = json.dumps(details)
        self.details = details_json

    def get_details(self):
        # Convert the JSON string back to a dictionary
        if self.details:
            return json.loads(self.details)
        return None

    def __str__(self):
        return f"{self.user.username} - {self.city}, {self.country}"

class Otp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    timestamp = models.DateTimeField(auto_now_add=True)
    validUntil = models.DateTimeField(default=timezone.now() + timezone.timedelta(minutes=5))