from django.contrib import admin
from django.contrib.admin.models import LogEntry

from Staff.models import *

class UserAdmin(admin.ModelAdmin):
    list_per_page = 50
    filter_horizontal = (
        'user_permissions',
        'groups',
    )
    search_fields = (
        'name',
        'username',
    )
    list_display = [
        "username",
        "name",
        "email",
        "date_joined",
        "dob",
    ]

admin.site.register(User, UserAdmin)