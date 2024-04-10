from django.urls import include,path
from Staff import views

urlpatterns = [
    path("register", views.register),
    path("login", views.login),
    path("logout", views.logout),
    path("checkToken", views.checkToken),
    path("resendOtp", views.resendOtp),
    path("getactivitylogs", views.getActivityLogs),
    path("getresults", views.getResults),
    path("getusercredit", views.getUserCredit),
    path("pay", views.pay),
    path("gettransactions", views.getTransactions),
    path("searchusers", views.searchUsers),
]
