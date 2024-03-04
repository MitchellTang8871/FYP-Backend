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
        "emailVerified",
        "date_joined",
    ]

class LogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', "description", 'timestamp')
    search_fields = ('user__username', 'action')
    list_filter = ('timestamp',)

class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'receiver', "amount", 'description', 'timestamp')
    search_fields = ('user__username', 'receiver__username')
    list_filter = ('timestamp',)

class UsualLoginLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'userIp', 'city', 'country', 'details', 'timestamp')
    search_fields = ('user__username', 'city', 'country')
    list_filter = ('timestamp',)

class OtpAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp', 'timestamp', 'validUntil')
    search_fields = ('user__username', 'otp')
    list_filter = ('timestamp',)

admin.site.register(User, UserAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(Transactions, TransactionsAdmin)
admin.site.register(UsualLoginLocation, UsualLoginLocationAdmin)
admin.site.register(Otp, OtpAdmin)