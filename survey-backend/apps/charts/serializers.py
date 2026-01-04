"""
Serializers for the charts app.
"""
from rest_framework import serializers
from .models import ChartSpec, UserSelection


class ChartSpecSerializer(serializers.ModelSerializer):
    """Serializer for ChartSpec model."""
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    dataset_filename = serializers.CharField(source='dataset.filename', read_only=True)
    dataset_uid = serializers.UUIDField(source='dataset.uid', read_only=True)
    
    class Meta:
        model = ChartSpec
        fields = [
            'uid',
            'owner',
            'owner_email',
            'dataset',
            'dataset_uid',
            'dataset_filename',
            'chart_type',
            'chart_config',
            'is_canonical',
            'derived_metrics',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'uid',
            'owner',
            'created_at',
            'updated_at',
        ]


class UserSelectionSerializer(serializers.ModelSerializer):
    """Serializer for UserSelection model."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    dataset_filename = serializers.CharField(source='dataset.filename', read_only=True)
    chart_type = serializers.CharField(source='selected_chart.chart_type', read_only=True)
    
    class Meta:
        model = UserSelection
        fields = [
            'uid',
            'user',
            'user_email',
            'dataset',
            'dataset_filename',
            'selected_chart',
            'chart_type',
            'note',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'uid',
            'user',
            'created_at',
            'updated_at',
        ]


class ChartSelectionInputSerializer(serializers.Serializer):
    """Serializer for selecting a chart."""
    chart_id = serializers.UUIDField(
        required=True,
        help_text="UID of the chart to select"
    )
    note = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional note about the selection"
    )
