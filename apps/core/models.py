from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Video(models.Model):
    SOURCE_TYPE_CHOICES = [
        ('local', 'Local'),
        ('youtube', 'YouTube'),
    ]

    video_id = models.AutoField(primary_key=True)  # Automatically increments
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ForeignKey to User model
    video_url = models.URLField(max_length=200, null=True, blank=True)  # URL to local video file
    youtube_url = models.URLField(max_length=200, null=True, blank=True)  # URL of YouTube video
    source_type = models.CharField(max_length=10, choices=SOURCE_TYPE_CHOICES)  # Enum-like field
    title = models.CharField(max_length=200)  # Title of the video
    description = models.TextField(null=True, blank=True)  # Description of the video
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when uploaded
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for last update

    def __str__(self):
        return self.title