# users/urls.py
from django.urls import path

app_name = 'users'  # This defines the app name for the namespace
from .views import *

urlpatterns = [
    path('auth/phone/send-otp/', send_otp, name='send-otp'),
    path('auth/phone/verify-otp/', verify_otp, name='verify-otp'),
]
