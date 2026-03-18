from django.utils.translation import gettext_lazy as _
from rest_framework import status
from .models import User, UserDetail, RolePermission
from .serializers import *
from ..utility import create_jwt_token, create_tokens
from rest_framework.response import Response
from .utils import *
import logging
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

from ..utils.decorators import *
from ..utils.custom_exceptions import *
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import OpenApiParameter, extend_schema


logger = logging.getLogger(__name__)


@csrf_exempt
@extend_schema(request=SendOtpSerializer,)
@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    """
    Sends an OTP to the provided phone number for login verification.
    """
    logger.info("Received send OTP request")
    try:
        serializer = SendOtpSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error("Bad request: %s", serializer.errors)
            raise InvalidRequestException(serializer.errors)
        phone = serializer.validated_data['phone_number']
        user = send_verify_phone(phone)
        token = create_jwt_token({"phone_number": user.phone_number})
        return Response({"message": "Verification code sent to phone number.", "token": token}, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error("Error sending OTP: %s", e)
        raise InvalidRequestException(e)

@extend_schema(request=VerifyOtpSerializer,)
@api_view(['POST'])
@permission_classes([AllowAny])
@parameters_required(keys=["token", "code"])
def verify_otp(request):
    """
    Verifies the OTP entered by the user and register the user.
    """
    logger.info("Received OTP verification request.")
    serializer = VerifyOtpSerializer(data=request.data)
    if not serializer.is_valid():
        logger.error("Bad request: %s", serializer.errors)
        raise InvalidRequestException(serializer.errors)
    try:
        phone = decode_jwt_token(serializer.validated_data['token'])['phone_number']
        code = serializer.validated_data['code']
        user = verify_phone(phone, code)
        user_role = RolePermission.objects.filter(user=user).first()
        tokens = create_tokens(user)
        return Response({
                "message": "Phone number verified.",
                "user": {
                    "access_token": tokens['access'],
                    "refresh_token": tokens['refresh'],
                    "access_time" : tokens['accessTokenExpiry'],
                    "refresh_time" : tokens['refreshTokenExpiry'],
                    "user_type":user_role.role,
                    "status":user.status,
                }
                
                }, status=status.HTTP_200_OK)   
    except Exception as e:
        logger.error("Error verifying OTP: %s", e)            
        raise InvalidRequestException(e)
    
@extend_schema(request=TokenRefreshSerializer,)
@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh(request):
    """
    Custom view to refresh access and refresh tokens using serializer validation.
    """
    serializer = TokenRefreshSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    token = serializer.token
    access = token.access_token

    return Response({
        "access_token": str(access),
        "refresh_token": str(token),  # RefreshToken string representation
        "access_time": int(access['exp']) * 1000,
        "refresh_time": int(token['exp']) * 1000,
    }, status=status.HTTP_200_OK)

