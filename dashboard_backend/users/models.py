
from typing import ClassVar

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
import uuid

from .manager import UserManager
from ..models import BaseModel

class User(AbstractBaseUser, PermissionsMixin):
    """
    Default custom user model for dashboard-backend.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """
    guid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    status = models.CharField(max_length=20, default="CREATED")
    username = models.CharField(max_length=150, unique=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()
    
    def __str__(self):
        return self.username + " - " + self.status


class UserDetail(BaseModel):
    """
    User profile details model with OneToOne relationship to User.
    Contains additional information about the user.
    """
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_detail')
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    education = models.CharField(max_length=100, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_image = models.TextField(blank=True, null=True)
    
    class Meta:
        app_label = "users"
        db_table = "user_detail"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def __str__(self):
        name = self.get_full_name().strip() or "Unnamed User"
        gender = self.gender or "N/A"
        dob = self.date_of_birth.strftime("%Y-%m-%d") if self.date_of_birth else "N/A"
        return f"{name} - {gender} - {dob}"


class Address(BaseModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address')
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    class Meta:
        app_label = "users"
        db_table = "address"
    
    def __str__(self):
        state = self.state or "N/A"
        city = self.city or "N/A"
        country = self.country or "N/A"
        pincode = self.pincode or "N/A"
        return f"{state} - {city} - {country} - {pincode}"

class RolePermission(BaseModel):
    id = models.BigAutoField(primary_key=True)
    class Role(models.TextChoices):            
        ADMINISTRATOR = "administrator", "Administrator"
        MANAGER = "manager", "Manager" 
        CLIENT = "client", "Client"
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_permissions')
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CLIENT)
    class Meta:
        app_label = "users"
        db_table = "role_permissions"
    
    def __str__(self):        
        role = self.role or "N/A"
        return f"{role}"
