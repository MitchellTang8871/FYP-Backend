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
    ]

class LogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    search_fields = ('user__username', 'action')
    list_filter = ('timestamp',)

class UsualLoginLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'userIp', 'city', 'country', 'details', 'timestamp')
    search_fields = ('user__username', 'city', 'country')
    list_filter = ('timestamp',)

admin.site.register(User, UserAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(UsualLoginLocation, UsualLoginLocationAdmin)