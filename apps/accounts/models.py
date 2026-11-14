import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

# Create your models here.
class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None  # Remove the username field
    email = models.EmailField(unique=True,db_index=True)  # Use email as the unique identifier
    phone_number = models.CharField(max_length=15,unique=True, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    
    objects = CustomUserManager()  # Use the custom user manager
    
    USERNAME_FIELD = 'email'  # Set email as the USERNAME_FIELD
    REQUIRED_FIELDS = []  # No additional required fields
    
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']  # Order users by date joined in descending order