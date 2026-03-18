from rest_framework import status
from rest_framework.exceptions import APIException


class NseFetchException(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_code = "NSE_FETCH_FAILED"
    default_detail = "Failed to fetch data from NSE."


class NseParseException(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_code = "NSE_PARSE_FAILED"
    default_detail = "Received unexpected data format from NSE."


class NiftySnapshotNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "NIFTY_SNAPSHOT_NOT_FOUND"
    default_detail = "No Nifty snapshot found."

