from django import views
from django.urls import path
from .views import login_view
from . import views

urlpatterns = [
    path('login/', login_view, name='login'),
    path("cameras/", views.camera_list),
    path("alerts/", views.alert_list),
    path("alerts/create/", views.create_alert),
]