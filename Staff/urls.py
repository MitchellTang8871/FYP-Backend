from django.urls import include,path
from Staff import views

urlpatterns = [
    path("register", views.register),
]
