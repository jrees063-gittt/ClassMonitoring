from django.db import models

class Camera(models.Model):
    hall_name = models.CharField(max_length=100)
    camera_name = models.CharField(max_length=100)
    risk_level = models.CharField(
        max_length=10,
        choices=[("low","Low"),("medium","Medium"),("high","High")],
        default="low"
    )
    status_message = models.CharField(max_length=200, default="Normal")

    def __str__(self):
        return f"{self.hall_name} - {self.camera_name}"


class Alert(models.Model):
    student_name = models.CharField(max_length=100)
    hall = models.CharField(max_length=100)
    violation_type = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    evidence_image = models.ImageField(upload_to="alerts/", null=True, blank=True)

    def __str__(self):
        return f"{self.student_name} - {self.violation_type}"