import re
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(AbstractUser):
    USERNAME_FIELD = "username"

    username = models.CharField(max_length=24, unique=True)
    name = models.CharField(default="Anonymous", max_length=120)
    email = models.CharField(default=None, max_length=100, null=True, blank=True)
    # profileImage = models.ImageField(
    #     max_length=500,
    #     upload_to=get_image_path,
    #     blank=True,
    #     null=True,
    #     help_text="In proportion of 200 x 200 pixels",
    #     validators=[
    #         RegexValidator("^[a-zA-Z0-9!@#$&()_\\-`.+,/\"]*$", message="The name of the image should only contain alphabets and numbers", code="Invalid image name")
    #     ],
    # )
    dob = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.name is not None:
            self.name = re.sub(r" +", " ", self.name).strip()

        if self.name == "":
            self.name = None

        if self.email == "":
            self.email = None

        super(User, self).save(*args, **kwargs)