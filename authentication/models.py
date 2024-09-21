from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)  
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)  
    
    def __str__(self):
        return self.name