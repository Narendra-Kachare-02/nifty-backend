import copy
import logging

from django.utils import timezone
from more_itertools import take
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from request_id.middleware import generate_request_id

logger = logging.getLogger(__name__)

def rest_exception_handler(exc, context):
    logger.debug('Custom exception handler invoked')
    
    # Handle JWT authentication errors specifically
    if isinstance(exc, (InvalidToken, TokenError)):
        logger.warning(f"JWT authentication error: {str(exc)}")
        response = exception_handler(exc, context)
        if response:
            response.data = {
                'message': response.data['messages'][0]['message'],
                'error_code': 'INVALID_TOKEN',
                'http_status_code': 401,
                'severity': 'ERROR',
                'request_id': generate_request_id(),
                'timestamp': timezone.now(),
                'path': context['request'].get_full_path(),
            }
        return response
    # Example response.data for JWT authentication error
#     {
#     "message": "Invalid or expired token",
#     "error_code": "INVALID_TOKEN",
#     "http_status_code": 401,
#     "severity": "ERROR",
#     "request_id": "8f556d7f-f115-468c-a011-c91433d60125",
#     "timestamp": "2025-09-14T16:45:48.615295Z",
#     "path": "/api/events/",
#     "response": {
#         "detail": "Given token not valid for any token type",
#         "code": "token_not_valid",
#         "messages": [
#             {
#                 "token_class": "AccessToken",
#                 "token_type": "access",
#                 "message": "Token is invalid or expired"
#             }
#         ]
#     }
# }
    
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now modify the response to desired changes.
    if response is not None and 'request' in context:
        """For authenticated clients, include the error details for Django errors."""

        exception_data = copy.deepcopy(response.data)
        """non_field_errors: Are the internal errors thrown by Django Serializer for form validations."""

        if 'non_field_errors' in response.data:
            response.data.clear()
            if isinstance(exception_data['non_field_errors'], (list, tuple)):
                response.data['message'] = exception_data['non_field_errors'][0]
            else:
                response.data['message'] = exception_data['non_field_errors']
        elif 'detail' in response.data:
            response.data.clear()
            response.data['message'] = exception_data['detail']
        elif isinstance(response.data, dict):
            first_error = take(1, response.data.items())
            response.data.clear()
            if isinstance(first_error[0][1], list):
                response.data['message'] = first_error[0][0] + ": " + first_error[0][1][0]
            elif isinstance(first_error[0][1], dict):
                response.data['message'] = first_error[0][0] + ": " + list(first_error[0][1].values())[0][0]
        else:
            response.data.clear()
            response.data['message'] = exception_data

        response.data['request_id'] = generate_request_id()
        response.data['http_status_code'] = response.status_code
        response.data['error_code'] = response.status_text
        set_severity(response)
        response.data['timestamp'] = timezone.now()
        response.data['path'] = context['request'].get_full_path()

    # logger.error('error_message: {}'.format(str(response.data.get('message', None))))
    return response


def set_severity(response):
    """Sets severity for error response based on status code"""

    if response.status_code == 500:
        response.data['severity'] = "FATAL"
    else:
        response.data['severity'] = "ERROR"
