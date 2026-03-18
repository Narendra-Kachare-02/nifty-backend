from functools import wraps
from django.http import JsonResponse
from .custom_exceptions import *
from ..utility import decode_jwt_token
import logging
import json
from django.core.cache import cache
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from ..users.models import RolePermission

logger = logging.getLogger(__name__)

def get_token_from_request(request):
    # Check the Authorization header
    logger.info(f"Processing request method: {request.method}, URL: {request.path}")
    auth_header = request.headers.get('Authorization')
    if auth_header:
        logger.info(f"Authorization header found: {auth_header}")
        if auth_header and auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            logger.info(f"Token found in Authorization header: {token_key}")
            return token_key
        else:
            logger.warning("Authorization header present, but does not start with 'Token '")
    else:
        logger.info("No Authorization header found")

    # Check the query parameters
    token_key = request.GET.get('token')
    if token_key:
        logger.info(f"Token found in query parameters: {token_key}")
        return token_key
    else:
        logger.info("No token found in query parameters")

    # Check the JSON body
    if request.content_type == 'application/json':
        try:            
            body = json.loads(request.body)
            token_key = body.get('token')
            if token_key:
                logger.info(f"Token found in JSON body: {token_key}")
                return token_key
            else:
                logger.warning("No 'token' field found in JSON body")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON body: {str(e)}")
            pass
    logger.info("No token found in request")
    return None

def get_parameters_from_body(request):    
    if request.content_type == 'application/json':
        try:            
            body = json.loads(request.body)                
            return body
        except json.JSONDecodeError:
            raise InvalidRequestException("Invalid json request.")    
    else: 
        return None
    

def check_keys(dictionary, keys):    
    result = [key for key in keys if key not in dictionary]
    return result



def token_required(keys=["phone_number"]):
    def decorator(view_func):            
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            logger.info(f"Checking token for {keys}")
            token_key = get_token_from_request(request)
            if not token_key:
                logger.info("Token key not found")
                raise TokenException("Token not found.")
            token_info = decode_jwt_token(token_key)
            if not token_info:
                logger.info("Token info not found")
                raise TokenException("Token is not valid.")
            missing_keys = check_keys(token_info, keys)
            if not missing_keys :                        
                return view_func(request, *args, **kwargs)
            else:
                raise TokenException(f"Missing property: {keys}")
        return _wrapped_view
    return decorator

def parameters_required(keys=[]):
    def decorator(view_func):            
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            logger.info("Checking body for %s", keys)
            body = get_parameters_from_body(request)
            if not body:
                logger.error("Missing body")
                raise InvalidRequestException("Missing body.")            
            missing_keys = check_keys(body, keys)
            if not missing_keys:                        
                return view_func(request, *args, **kwargs)
            else:
                logger.error("Missing property: %s", missing_keys)
                raise InvalidRequestException(f"Missing property: {missing_keys}")
        return _wrapped_view
    return decorator


# Role hierarchy from lowest to highest
ROLE_HIERARCHY = [
    RolePermission.Role.CLIENT,
    RolePermission.Role.MANAGER,
    RolePermission.Role.ADMINISTRATOR,
]

def check_role_permission(user_role, required_role):
    """
    Check if the user's role is higher or equal to the required role.
    Raises RolePermissionDenied if the user's role is insufficient.
    """
    try:
        user_index = ROLE_HIERARCHY.index(user_role)
        required_index = ROLE_HIERARCHY.index(required_role)
    except ValueError as e:
        logger.error(f"Invalid role encountered: {e}")
        raise RolePermissionError("Invalid role found during permission check.")
    logger.info(f"Checking role: user='{user_role}' (idx={user_index}), required='{required_role}' (idx={required_index})")
    if user_index < required_index:
        logger.error("Access denied")
        raise RolePermissionDenied(f"Access denied: The user's role '{user_role}' does not meet the required role '{required_role}' to perform this action.")
    return True
    


def role_required(required_role):
    """
    Decorator to restrict access to views based on the user's role hierarchy.
    Raises custom exceptions for error handling.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            logger.info("Role Required decorator invoked")
            user_role = RolePermission.objects.filter(user=request.user).first()
            if not user_role:
                logger.warning(f"No role assigned to user '{request.user}'.")
                raise RolePermissionDenied("Access denied: No role assigned to the user.")
            user_role = user_role.role
            logger.info(f"User '{request.user}' has role '{user_role}'.")
            # Check the role against the hierarchy
            if check_role_permission(user_role, required_role):
                logger.info(f"User '{request.user}' authorized to access '{view_func.__name__}'.")
                return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
