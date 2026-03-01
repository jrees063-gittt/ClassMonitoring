from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from requests import Response

from monitoring.models import Camera
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Camera, Alert
from .serializers import CameraSerializer, AlertSerializer



@csrf_exempt
def login_view(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    username = data.get("username")
    password = data.get("password")

    user = authenticate(request, username=username, password=password)

    if user:
        login(request, user)
        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

# Get all cameras
@api_view(["GET"])
def camera_list(request):
    cameras = Camera.objects.all()
    serializer = CameraSerializer(cameras, many=True)
    return Response(serializer.data)


# Get all alerts
@api_view(["GET"])
def alert_list(request):
    alerts = Alert.objects.all().order_by("-timestamp")
    serializer = AlertSerializer(alerts, many=True)
    return Response(serializer.data)


# AI system sends alert here
@api_view(["POST"])
def create_alert(request):

    serializer = AlertSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        # Update camera risk automatically
        hall = request.data.get("hall")
        violation = request.data.get("violation_type")

        camera = Camera.objects.filter(hall_name=hall).first()
        if camera:
            camera.risk_level = "high"
            camera.status_message = violation
            camera.save()

        return Response({"status": "Alert Created"})

    return Response(serializer.errors, status=400)