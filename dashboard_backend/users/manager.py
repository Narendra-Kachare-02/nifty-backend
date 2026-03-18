from typing import TYPE_CHECKING, Union

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager

if TYPE_CHECKING:
    from .models import User  # noqa: F401


class UserManager(DjangoUserManager["User"]):
    """Custom manager for the User model."""

    def _create_user(
        self,
        username: str | None = None,
        email: str | None = None,
        phone_number: str | None = None,
        password: str | None = None,
        **extra_fields
    ):
        """
        Create and save a user with the given email and password.
        """
        # Validate that at least one identifier is provided
        if not email and not phone_number and not username:
            raise ValueError("Provide either email or phone number")
        # Set username based on available identifier
        if email:
            username = email
        elif phone_number:
            username = phone_number
            
        # Normalize email if provided
        if email:
            email = self.normalize_email(email)
            
        user = self.model(
            username=username,
            phone_number=phone_number,
            email=email,
            **extra_fields
        )
        
        user.set_password(password)
            
        user.save(using=self._db)
        return user

    def create_user(
        self,
        username: str | None = None,
        email: str | None = None,
        phone_number: str | None = None,
        password: str | None = None,
        **extra_fields
    ):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(
            username=username,
            email=email,
            phone_number=phone_number,
            password=password,
            **extra_fields
        )

    def create_superuser(
        self,
        username: str | None = None,
        email: str | None = None,
        phone_number: str | None = None,
        password: str | None = None,
        **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(
            username=username,
            email=email,
            phone_number=phone_number,
            password=password,
            **extra_fields
        )