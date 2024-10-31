from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Video(models.Model):
    SOURCE_TYPE_CHOICES = [
        ('local', 'Local'),
        ('youtube', 'YouTube'),
    ]

    video_id = models.AutoField(primary_key=True)  
    yt_video_id = models.CharField(max_length=200, unique=True, null=True, blank=True) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    video_url = models.URLField(max_length=200, null=True, blank=True) 
    youtube_url = models.URLField(max_length=200, null=True, blank=True) 
    artist = models.CharField(max_length=200, default=None, null=True, blank=True)  
    source_type = models.CharField(max_length=10, choices=SOURCE_TYPE_CHOICES)
    title = models.CharField(max_length=200)  
    description = models.TextField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    is_downloaded = models.BooleanField(default=False)

    def __str__(self):
        return self.title