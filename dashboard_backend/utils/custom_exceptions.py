import logging
import random

from rest_framework import status
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)

def get_default_messages_403():
    unauthorized_messages = [
            "Sorry, jammed up right now. Who dis?",
            "Can't chat right now, who's this?",
            "Yo, sorry, unfamiliar number. Who dis?",
            "Yo! New number, who's texting?",
            "Hey there! Sorry, got a lot going on. Who's reaching out?",
            "Apologies, caught up at the moment. Who's this?",
            "Hey, apologies, not recognizing the number. Who's on the line?",
            "Hey! Busy right now. Mind sharing who's texting?",
            "Sorry, not ringing a bell. Who's hitting me up?",
            "Hey, sorry, not in the loop. Who's texting?",
            "Oops, unfamiliar number. Who's reaching out?",
            "Hey, not picking up on this one. Who's texting?",
            "Hey, apologies, name's slipping my mind. Who's this?",
            "Oops, sorry, blanking on who's texting. Mind refreshing my memory?",]
    random_message = random.choice(unauthorized_messages)
    return random_message




class DeviceTokenAlreadyExistsException(APIException):
    """Exception raised when a device with the same device token already exists."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A device with this token already exists.'
    default_code = 'device_token_exists'

class DeviceValidationException(APIException):
    """General validation exception for device data."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid device data.'
    default_code = 'device_validation_error'

class UserNotAuthenticatedException(APIException):
    """Exception raised when a user is not authenticated."""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'User authentication is required.'
    default_code = 'user_not_authenticated'

class UserAlreadyFoundException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "USER_ALREADY_FOUND"
    default_detail = "The user is already found."
    
class TwilioServiceException(APIException):
    status_code = 400
    default_detail = "A Twilio service error occurred."
    default_code = "twilio_error"


class PhoneVerificationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST  # or any other HTTP status code
    default_detail = 'There was an error with phone number verification.'
    default_code = 'phone_verification_error'
    
class InvalidTokenFormatException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'The provided token format is invalid. The token must have 3 parts separated by dots.'
    default_code = 'invalid_token_format'
    
class InvalidTokenException(APIException):
    """Exception raised when the provided token is invalid or expired."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid or expired token."
    default_code = "invalid_token"


class OTPVerificationException(APIException):
    """Exception raised for OTP verification errors."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Failed to send verification code."
    default_code = "otp_verification_failed"

class UserNotFoundException(APIException):
    """Exception raised when the user is not found in the database."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "User not found."
    default_code = "user_not_found"

class PhoneNumberValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'There was an error validating the phone number.'
    default_code = 'phone_number_invalid'


class RolePermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'role_permission_denied'

class RolePermissionError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Invalid role found during permission check.'
    default_code = 'role_permission_error'

class InvalidRoleError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'User does not have the required role.'
    default_code = 'invalid_role'

class CustomPermissionDenied(APIException):
    """This represents the access denied/permission denied exception"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = get_default_messages_403()
    default_code = None


class CustomNotFound(APIException):
    """This represents the not found exception"""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Not Found.'
    default_code = None


class CustomGone(APIException):
    """This represents the gone exception"""

    status_code = status.HTTP_410_GONE
    default_detail = 'Gone.'
    default_code = None


class CustomBadRequest(APIException):
    """This represents the bad request exception"""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad Request.'
    default_code = None


class CustomPreconditionFailed(APIException):
    """This represents the pre-condition failed exception"""

    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_detail = 'Precondition Failed'
    default_code = None


class CustomTooEarly(APIException):
    """This represents the too early exception"""

    status_code = 425
    default_detail = 'Too Early.'
    default_code = None


class CustomNotAcceptable(APIException):
    """This represents the conflict exception"""

    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = 'Not Acceptable.'
    default_code = None


class CustomConflictRequest(APIException):
    """This represents the conflict exception"""

    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Conflict Error.'
    default_code = None


class CustomInternalServerError(APIException):
    """This represents the internal server error"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Internal Server Error.'
    default_code = None


class CustomGatewayTimeoutError(APIException):
    """This represents the gateway timeout error"""
    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    default_detail = 'Timeout Error.'
    default_code = None


class BadGatewayException(APIException):
    """Upstream/FastAPI service error (502)."""
    status_code = 502
    default_detail = 'Upstream service error.'
    default_code = None


class TokenException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "TOKEN_NOT_FOUND"
    default_detail = "Token not found."

class InvalidSerializerException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "INVALID_SERIALIZER"
    default_detail = "Invalid serializer."   

class InvalidRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "TOKEN_NOT_FOUND"
    default_detail = "Token not found."    

class AuthenticationFailureException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = "AUTHENTICATION_FAILURE"
    default_detail = "Failed to authenticate the user."    

class UnauthorizedAccess(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "UNAUTHORIZED_ACCESS"
    default_detail = "User is not authorized to access."    

    
class TwilioPhoneVerificationException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_code = "PHONE_VERIFICATION_FAILED"
    default_detail = "Failed to validate the user's phone number."    

class TicketCreationFailed(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_code = "TICKET_CREATION_FAILED"
    default_detail = "Failed to create the support ticket."    


class GenericValidationException(APIException):
    """This represents the Generic Validation e.g. ValidationError, etc"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred'

    def __init__(self, detail, field, status_code):
        if status_code is not None:
            self.status_code = status_code

        if detail is not None:
            self.detail = {field: str(detail)}
        else:
            self.detail = {'detail': str(self.default_detail)}
