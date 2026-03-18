from rest_framework import serializers

from .models import NiftySnapshot


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

