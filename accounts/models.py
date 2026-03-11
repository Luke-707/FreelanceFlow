from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('freelancer', 'Freelancer'),
        ('client', 'Client'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='freelancer')
    
    def is_freelancer(self):
        return self.role == 'freelancer'
    
    def is_client(self):
        return self.role == 'client'
