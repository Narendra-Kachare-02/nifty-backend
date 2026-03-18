from rest_framework import serializers

from .models import NiftySnapshot, OptionChainSnapshot, NiftyChartSnapshot


class NiftySnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = NiftySnapshot
        fields = [
            "captured_at",
            "source_lastUpdateTime",
            "name",
            "advance",
            "timestamp",
            "marketStatus",
            "metadata",
            "data",
        ]


class OptionChainSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionChainSnapshot
        fields = [
            "captured_at",
            "symbol",
            "expiryDate",
            "payload",
        ]


class NiftyChartSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = NiftyChartSnapshot
        fields = ["captured_at", "indexName", "flag", "payload"]
