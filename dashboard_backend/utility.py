from datetime import datetime, timedelta, timezone
from django.conf import settings
import jwt
from twilio.base.exceptions import TwilioRestException, TwilioException
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import logging
from twilio.rest import Client
from rest_framework_simplejwt.tokens import RefreshToken
from dashboard_backend.utils.custom_exceptions import TwilioServiceException, TwilioPhoneVerificationException, CustomNotFound

logger = logging.getLogger(__name__)

# JWT Utility Functions
def create_jwt_token(data, timedelta_in_min = 60 ):
    payload = {        
        'exp': datetime.now(timezone.utc) + timedelta(minutes=timedelta_in_min),
        'iat': datetime.now(timezone.utc)
    }
    payload.update(data)
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')
    return token


def create_tokens(user):
    """Generates access and refresh tokens for the authenticated user."""
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    
    return {
        'access': str(access),
        'refresh': str(refresh),
        'accessTokenExpiry': int(access['exp']) * 1000,   # in milliseconds
        'refreshTokenExpiry': int(refresh['exp']) * 1000        # in milliseconds
    }


def decode_jwt_token(token):
    try:
        logger.info("Decoding token invoked")
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        logger.info(f"Token decoded successfully. Payload: {payload}")
        
        return payload
    except ExpiredSignatureError as e:
        logger.warning(f"Failed to decode a token, {str(e)} ")
        return None
    except InvalidTokenError as e:
        logger.warning(f"Failed to decode a token, {str(e)} ")
        return None
    
def send_verification_code(phone_number):
    try:
        logger.info(f"Sending verification code: {phone_number}")
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        verification = client.verify.services(settings.VERIFICATION_SID).verifications.create(to=f'{phone_number}', channel='sms')
        logger.info(f"Verification code sent to {phone_number}. Status: {verification.status}")
        return verification
    except TwilioRestException as e:
        logger.error("Twillio service exception occurs")
        raise TwilioServiceException(f"Twilio error occur : {e}")
    except TwilioException as e:
        logger.error("Twillio service exception occurs")
        raise TwilioServiceException(f"Twilio error occur : {e}")
    except Exception as e:
        logger.error(f"Failed to send the verification code.\nError: {e}")
        raise TwilioPhoneVerificationException("Failed to send the verification code.")
            
    
def verify_otp(phone_number, code):
    try:
        logger.info(f"Verifying the phone number: {phone_number}")
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        verification_check = client.verify.services(settings.VERIFICATION_SID).verification_checks.create(to=phone_number, code=code)
        return verification_check
    except TwilioRestException as e:
        logger.error("Twillio service exception occurs")
        raise TwilioServiceException(f"Twilio error occur : {e}")
    except TwilioException as e:
        logger.error("Twillio service exception occurs")
        raise TwilioServiceException(f"Twilio error occur : {e}")
    except Exception as e:
        logger.error(f"Phone verification failed for user {phone_number}.", e)
        raise TwilioPhoneVerificationException(f"Phone verification failed for user {phone_number}.")
            

def get_object_or_404_custom(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        logger.error(f"{model.__name__} not found with args: {args} and kwargs: {kwargs}")
        raise CustomNotFound(f'{model.__name__} not found.')
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching {model.__name__}: {e}")
        raise CustomNotFound(f'An unexpected error occurred: {e}')


file_schema = {
        "multipart/form-data": {
            "type": "object",
            "required": ["file"],
            "properties": {
                "file": {"type": "string", "format": "binary", "description": "Agreement document (any file type)"},
            },
        }
    }