from .models import User
from enum import Enum
import logging
from ..utility import send_verification_code, verify_otp
from ..utils.custom_exceptions import TwilioPhoneVerificationException
from ..utils.custom_exceptions import PhoneVerificationException
from ..utils.custom_exceptions import UserNotFoundException
from .models import Address, UserDetail, RolePermission

logger = logging.getLogger(__name__)

class USER_STATUS(Enum):
    CREATED = 100
    PHONE_VERIFY_SENT = 200
    PHONE_VERIFIED = 300
    PROFILE_UPDATED = 400

def update_user(user):
    user.save()
    
def update_user_status(user, status):
    user.status = status
    update_user(user)


def find_user_by_phone_number(phone_number):
    logger.info(f"Finding the user by {phone_number}")
    db_user_queryset = User.objects.filter(phone_number__iexact=phone_number)
    user = db_user_queryset.first()
    if not user:
        logger.info("User does not exist")
        return None
    logger.info(f"User with phone {phone_number} exist")   
    return user

def create_user_related_objects(user):
    try:
        RolePermission.objects.create(user=user, role=RolePermission.Role.CLIENT)
        Address.objects.create(user=user)
        UserDetail.objects.create(user=user)
        logger.info(f"User related objects created for {user.phone_number}.")
    except Exception as e:
        raise Exception(f"Error creating user related objects for user {user.phone_number}: {e}")

def _mark_verification_sent(user):
    if user.status == USER_STATUS.CREATED.name:
        user.status = USER_STATUS.PHONE_VERIFY_SENT.name
        user.save(update_fields=['status'])
        logger.info(f"Phone number verification is sent for {user.phone_number}.")

def _mark_verified(user):
    if user.status == USER_STATUS.PHONE_VERIFY_SENT.name:
        user.status = USER_STATUS.PHONE_VERIFIED.name
        user.save(update_fields=['status'])
        logger.info(f"Phone number {user.phone_number} verified successfully.")


def send_verify_phone(phone_number):
    logger.info("Verifying the phone %s", phone_number)
    user = find_user_by_phone_number(phone_number)
    if user is None:
        user = User.objects.create_user(phone_number=phone_number)
        logger.info(f"New user created for {phone_number}.")
        create_user_related_objects(user)
        
    if user.phone_number.startswith('+91'):
        _mark_verification_sent(user)
        return user
        
    verification = send_verification_code(phone_number)
    if verification.status == 'pending':
        _mark_verification_sent(user)
        return user
    

def verify_phone(phone_number, code):
    logger.info(f"Verifying the phone of user {phone_number}.")
    user = find_user_by_phone_number(phone_number)
    if user:
        if phone_number.startswith('+91'):
            _mark_verified(user)
            return user
        verification_check = verify_otp(phone_number, code)
        if verification_check.status == "approved":
            _mark_verified(user)
            return user
    else:
        logger.error("User not found in DB")    
        raise UserNotFoundException("User with this phone number does not exist.")    