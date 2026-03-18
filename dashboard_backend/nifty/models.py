from django.db import models
from django.utils import timezone


class NiftySnapshot(models.Model):
    captured_at = models.DateTimeField(default=timezone.now, db_index=True)
    source_lastUpdateTime = models.CharField(max_length=64, null=True, blank=True, db_index=True)

    name = models.CharField(max_length=64, null=True, blank=True)
    advance = models.JSONField(default=dict)
    timestamp = models.CharField(max_length=64, null=True, blank=True)

    marketStatus = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict)
    data = models.JSONField(default=list)

    class Meta:
        db_table = "nifty_snapshot"
        indexes = [
            models.Index(fields=["-captured_at"]),
        ]

    def __str__(self) -> str:
        return f"NiftySnapshot(captured_at={self.captured_at.isoformat()})"


class OptionChainSnapshot(models.Model):
    captured_at = models.DateTimeField(default=timezone.now, db_index=True)

    symbol = models.CharField(max_length=32, default="NIFTY", db_index=True)
    expiryDate = models.CharField(max_length=32, null=True, blank=True, db_index=True)

    # Keep keys as-is; store the full NSE response.
    payload = models.JSONField(default=dict)

    class Meta:
        db_table = "option_chain_snapshot"
        indexes = [
            models.Index(fields=["symbol", "-captured_at"]),
            models.Index(fields=["symbol", "expiryDate", "-captured_at"]),
        ]

    def __str__(self) -> str:
        return f"OptionChainSnapshot(symbol={self.symbol}, captured_at={self.captured_at.isoformat()})"


class NiftyChartSnapshot(models.Model):
    captured_at = models.DateTimeField(default=timezone.now, db_index=True)

    indexName = models.CharField(max_length=64, default="NIFTY 50", db_index=True)
    flag = models.CharField(max_length=8, db_index=True)  # 1D/1M/3M/6M/1Y

    payload = models.JSONField(default=dict)

    class Meta:
        db_table = "nifty_chart_snapshot"
        indexes = [
            models.Index(fields=["indexName", "flag", "-captured_at"]),
        ]

    def __str__(self) -> str:
        return f"NiftyChartSnapshot(indexName={self.indexName}, flag={self.flag}, captured_at={self.captured_at.isoformat()})"
