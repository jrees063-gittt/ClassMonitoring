from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


@csrf_exempt
def login_view(request):

    if request.method == "POST":
        data = json.loads(request.body)

        username = data.get("username")
        password = data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)   # creates session
            return JsonResponse({
                "status": "success",
                "message": "Login successful"
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "Invalid credentials"
            }, status=401)

    return JsonResponse({"error": "Invalid request"}, status=400)