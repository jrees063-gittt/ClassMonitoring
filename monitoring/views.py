from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Camera, Alert
from .utils import calculate_risk
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

# 🔥 Risk Scoring Map (put this above the function)
RISK_MAP = {
    "Looking Away": 2,
    "Multiple Faces": 5,
    "Phone Detected": 10,
    "Head Down Long": 3
}


@api_view(["POST"])
def create_alert(request):
    student = request.data.get("student_name")
    hall = request.data.get("hall")
    violation = request.data.get("violation_type")

    # 🔥 Get risk points from map
    points = RISK_MAP.get(violation, 1)

    # Save alert
    Alert.objects.create(
        student_name=student,
        hall=hall,
        violation_type=violation,
        risk_points=points
    )

    # Update camera risk
    camera = Camera.objects.filter(hall_name=hall).first()

    if camera:
        camera.risk_score += points
        camera.risk_level = calculate_risk(camera.risk_score)
        camera.last_violation = violation
        camera.save()

    # 🔥 WebSocket broadcast
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "dashboard",
        {
            "type": "send_update",
        }
    )

    return Response({"status": "Alert Created"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    cameras = Camera.objects.all()
    alerts = Alert.objects.order_by("-timestamp")[:10]

    return Response({
        "cameras": [
            {
                "hall": c.hall_name,
                "camera": c.camera_name,
                "risk_level": c.risk_level,
                "risk_score": c.risk_score,
                "last_violation": c.last_violation
            }
            for c in cameras
        ],
        "alerts": [
            {
                "student": a.student_name,
                "hall": a.hall,
                "violation": a.violation_type,
                "time": a.timestamp.strftime("%H:%M:%S")
            }
            for a in alerts
        ]
    })

from django.utils import timezone
from datetime import timedelta

@api_view(["GET"])
def analytics(request):
    today = timezone.now() - timedelta(days=1)

    total_alerts = Alert.objects.filter(timestamp__gte=today).count()
    high_risk = Camera.objects.filter(risk_level="High").count()

    return Response({
        "total_alerts": total_alerts,
        "high_risk_halls": high_risk
    })

