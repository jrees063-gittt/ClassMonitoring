from django.db import models


class Camera(models.Model):
    hall_name = models.CharField(max_length=100)
    camera_name = models.CharField(max_length=100)

    risk_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=20, default="Low")

    last_violation = models.CharField(max_length=200, blank=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hall_name} - {self.camera_name}"


class Alert(models.Model):
    student_name = models.CharField(max_length=100)
    hall = models.CharField(max_length=100)
    violation_type = models.CharField(max_length=100)
    risk_points = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.student_name} - {self.violation_type}"