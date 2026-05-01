from django.db import models
from django.contrib.auth.models import User

class Detection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='crop_images/')
    crop_type = models.CharField(max_length=100, blank=True)
    disease = models.CharField(max_length=100, blank=True)
    confidence = models.FloatField(default=0.0)
    recommendation = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    prevention = models.TextField(blank=True)
    care_tips = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crop_type} - {self.disease} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
