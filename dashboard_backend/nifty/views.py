import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from dashboard_backend.utils.custom_exceptions import CustomInternalServerError
from .serializers import NiftySnapshotSerializer, OptionChainSnapshotSerializer
from .services import getLatestNiftySnapshot, getLatestOptionChainSnapshot, getNiftySeries


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


@api_view(["GET"])
@permission_classes([AllowAny])
def latestOptionChain(request):
    """
    Thin view: request -> service -> serializer -> response.
    Optional query: expiryDate=...
    """
    try:
        expiry = request.query_params.get("expiryDate") or None
        snapshot = getLatestOptionChainSnapshot(symbol="NIFTY", expiryDate=expiry)
        serializer = OptionChainSnapshotSerializer(snapshot)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except APIException:
        raise
    except Exception as e:  # noqa: BLE001
        logger.exception("Option chain latest API failed")
        raise CustomInternalServerError(str(e))


@api_view(["GET"])
@permission_classes([AllowAny])
def niftySeries(request):
    """
    Chart-friendly series endpoint.
    Query: range=15M|30M|1H|1D (default 1D)
    """
    try:
        range_key = request.query_params.get("range") or "1D"
        series = getNiftySeries(range_key=range_key)
        return Response({"range": range_key, "series": series}, status=status.HTTP_200_OK)
    except APIException:
        raise
    except Exception as e:  # noqa: BLE001
        logger.exception("Nifty series API failed")
        raise CustomInternalServerError(str(e))
