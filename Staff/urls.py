from django.urls import include,path
from Staff import views

urlpatterns = [
    path("register", views.register),
    path("login", views.login),
    path("logout", views.auth_logout),
    path("checkToken", views.checkToken),
    path("resendOtp", views.resendOtp),
]
