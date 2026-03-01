# from django import views
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('login/', login_view, name='login'),
#     path("cameras/", views.camera_list),
#     path("alerts/", views.alert_list),
#     path("alerts/create/", views.create_alert),
# ]
from django.urls import path
from . import views

urlpatterns = [
    path("alerts/create/", views.create_alert),
    path("dashboard/", views.dashboard_data),
]