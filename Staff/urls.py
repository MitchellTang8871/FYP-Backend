from django.urls import include,path
from Staff import views

urlpatterns = [
    path("isadmin", views.isAdmin),
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
    path("deluser",views.delUser),
    path("searchusers", views.searchUsers),

    # ASC
    # path("login2", views.login2),
    # path("deluser",views.delUser2),
    # path("searchusers", views.searchUsers2),
]
