from django.db import models

# Create your models here.
from django.contrib.auth.models import User
import uuid


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    vendor_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Auto-generated unique ID


