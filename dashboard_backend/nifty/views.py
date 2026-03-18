import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from dashboard_backend.utils.custom_exceptions import CustomInternalServerError
from .config import NSE_CHART_FLAGS
from .models import NiftyChartSnapshot, NiftySnapshot, OptionChainSnapshot
from .serializers import NiftySnapshotSerializer, OptionChainSnapshotSerializer
from .exceptions import NiftySnapshotNotFound
from .services import (
    fetchNiftyPayload,
    fetchNiftyChartPayload,
    fetchOptionChainContractInfo,
    fetchOptionChainPayload,
    getLatestNiftySnapshot,
    getLatestOptionChainSnapshot,
    getNiftySeries,
    saveNiftyChartSnapshot,
    saveNiftySnapshot,
    saveOptionChainSnapshot,
)
from .utils import isMarketOpenNow


logger = logging.getLogger(__name__)

# Secret key for cron endpoint (set in environment)
import os
CRON_SECRET = os.environ.get("CRON_SECRET", "")


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
        res = getNiftySeries(range_key=range_key)
        return Response(res, status=status.HTTP_200_OK)
    except APIException:
        raise
    except Exception as e:  # noqa: BLE001
        logger.exception("Nifty series API failed")
        raise CustomInternalServerError(str(e))


@api_view(["POST"])
@permission_classes([AllowAny])
def bootstrap(request):
    """
    Rare-condition endpoint:
    - If market is CLOSED and DB is missing snapshots, fetch from NSE once and persist.
    - Frontend should always read from DB-polling APIs after this.
    """
    try:
        if isMarketOpenNow():
            return Response(
                {"performed": False, "reason": "market_open"},
                status=status.HTTP_200_OK,
            )

        performed: dict[str, list[str] | bool] = {
            "niftyLatest": False,
            "chartFlagsFetched": [],
            "optionChainFetched": False,
        }

        # Ensure at least one latest snapshot exists.
        if not NiftySnapshot.objects.order_by("-captured_at").values("id").first():
            payload = fetchNiftyPayload()
            saveNiftySnapshot(payload)
            performed["niftyLatest"] = True

        # Ensure chart snapshots exist for all flags.
        missing_flags = [
            flag for flag in NSE_CHART_FLAGS if not NiftyChartSnapshot.objects.filter(flag=flag).values("id").first()
        ]
        for flag in missing_flags:
            payload = fetchNiftyChartPayload(flag=flag)
            saveNiftyChartSnapshot(payload=payload, flag=flag)
            (performed["chartFlagsFetched"] if isinstance(performed["chartFlagsFetched"], list) else []).append(flag)

        # Ensure at least one option chain snapshot exists.
        if not OptionChainSnapshot.objects.filter(symbol="NIFTY").order_by("-captured_at").values("id").first():
            ci = fetchOptionChainContractInfo()
            expiry_dates = ci.get("expiryDates") if isinstance(ci, dict) else None
            expiry = expiry_dates[0] if isinstance(expiry_dates, list) and expiry_dates else None
            if expiry:
                payload = fetchOptionChainPayload(expiry=expiry)
                saveOptionChainSnapshot(payload=payload, symbol="NIFTY", expiryDate=expiry)
                performed["optionChainFetched"] = True

        return Response(
            {
                "performed": performed,
            },
            status=status.HTTP_200_OK,
        )
    except APIException:
        raise
    except Exception as e:  # noqa: BLE001
        logger.exception("Nifty bootstrap API failed")
        raise CustomInternalServerError(str(e))


@api_view(["POST"])
@permission_classes([AllowAny])
def cronFetchData(request):
    """
    Cron endpoint: Called by external cron service (e.g., cron-job.org) to fetch NSE data.
    Replaces Celery Beat for free tier deployment.
    
    Requires X-Cron-Secret header for authentication.
    Call every 1-5 minutes during market hours.
    """
    provided_secret = request.headers.get("X-Cron-Secret", "")
    
    # If CRON_SECRET is not set, allow access (for initial testing)
    # Once set, it must match
    if CRON_SECRET and provided_secret != CRON_SECRET:
        logger.warning(f"Cron auth failed. Expected length: {len(CRON_SECRET)}, Got length: {len(provided_secret)}")
        return Response(
            {"error": "Unauthorized", "hint": "X-Cron-Secret header doesn't match CRON_SECRET env var"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        result = {"market_open": False, "fetched": []}
        
        if not isMarketOpenNow():
            return Response(result, status=status.HTTP_200_OK)
        
        result["market_open"] = True

        # Fetch Nifty data
        try:
            payload = fetchNiftyPayload()
            saveNiftySnapshot(payload)
            result["fetched"].append("nifty")
            
            chart_payload = fetchNiftyChartPayload(flag="1D")
            saveNiftyChartSnapshot(chart_payload, flag="1D")
            result["fetched"].append("chart_1D")
        except Exception as e:
            logger.exception("Cron: Failed to fetch Nifty data")
            result["nifty_error"] = str(e)

        # Fetch Option Chain data
        try:
            contract = fetchOptionChainContractInfo()
            expiry_dates = contract.get("expiryDates") if isinstance(contract, dict) else None
            expiry = expiry_dates[0] if isinstance(expiry_dates, list) and expiry_dates else None
            if expiry:
                oc_payload = fetchOptionChainPayload(expiry=expiry)
                saveOptionChainSnapshot(oc_payload, symbol="NIFTY", expiryDate=expiry)
                result["fetched"].append("option_chain")
        except Exception as e:
            logger.exception("Cron: Failed to fetch Option Chain data")
            result["option_chain_error"] = str(e)

        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception("Cron fetch failed")
        raise CustomInternalServerError(str(e))
