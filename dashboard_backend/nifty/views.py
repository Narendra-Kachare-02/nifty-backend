import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from dashboard_backend.utils.custom_exceptions import CustomInternalServerError
from .serializers import NiftySnapshotSerializer
from .services import getLatestNiftySnapshot


logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([AllowAny])
def latest(request):
    """
    Thin view: request -> service -> serializer -> response.
    """
    try:
        snapshot = getLatestNiftySnapshot()
        serializer = NiftySnapshotSerializer(snapshot)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except APIException:
        # Keep intended status codes (e.g. 404 when no snapshot).
        raise
    except Exception as e:  # noqa: BLE001
        logger.exception("Nifty latest API failed")
        # Keep response shape consistent via global exception handler.
        raise CustomInternalServerError(str(e))

