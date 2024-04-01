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
    path("searchusers", views.searchUsers),
    path("pay", views.pay),
    path("gettransactions", views.getTransactions),
    path("deluser",views.delUser),

    # ASC
    # path("login2", views.login2),
    # path("searchusers2", views.searchUsers2),
    # path("deluser2",views.delUser2),
]
