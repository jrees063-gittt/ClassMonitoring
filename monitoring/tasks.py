from django.utils import timezone
from .models import Camera
from .utils import calculate_risk
from datetime import timedelta


def decay_risk():
    cameras = Camera.objects.all()

    for cam in cameras:
        if cam.last_update < timezone.now() - timedelta(minutes=2):
            cam.risk_score = max(0, cam.risk_score - 2)
            cam.risk_level = calculate_risk(cam.risk_score)
            cam.save()