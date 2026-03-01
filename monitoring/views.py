from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Camera, Alert
from .utils import calculate_risk
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@api_view(["POST"])
def create_alert(request):
    student = request.data.get("student_name")
    hall = request.data.get("hall")
    violation = request.data.get("violation_type")
    points = int(request.data.get("risk_points", 1))

    Alert.objects.create(
        student_name=student,
        hall=hall,
        violation_type=violation,
        risk_points=points
    )

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