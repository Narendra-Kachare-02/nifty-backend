from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from ..utils.custom_exceptions import InvalidTokenException
from rest_framework_simplejwt.exceptions import TokenError


class SendOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    
class VerifyOtpSerializer(serializers.Serializer):
    token = serializers.CharField()
    code = serializers.CharField(write_only=True)
  
class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value):
        try:
            self.token = RefreshToken(value)
        except TokenError:
            raise InvalidTokenException("Invalid or expired refresh token.")
        return value

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'country', 'pincode']
        
class UserDetailSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = UserDetail
        fields = ['first_name', 'last_name', 'education', 'profession', 'gender', 'date_of_birth', 'profile_image', 'address']
        