"""
Serializers for the ingest app.
"""
from rest_framework import serializers
from .models import UploadedDataset, ParsedRecord


class UploadedDatasetSerializer(serializers.ModelSerializer):
    """Serializer for UploadedDataset model."""
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    owner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UploadedDataset
        fields = [
            'uid',
            'owner',
            'owner_email',
            'owner_name',
            'filename',
            'mime_type',
            'size_bytes',
            'storage_path',
            'original_headers',
            'row_count',
            'parsed_ok',
            'error_message',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'uid',
            'owner',
            'storage_path',
            'original_headers',
            'row_count',
            'parsed_ok',
            'error_message',
            'created_at',
            'updated_at',
        ]
    
    def get_owner_name(self, obj):
        """Get owner's full name."""
        if hasattr(obj.owner, 'full_name'):
            return obj.owner.full_name
        return f"{obj.owner.firstname} {obj.owner.lastname}"


class DatasetUploadSerializer(serializers.Serializer):
    """Serializer for file upload."""
    file = serializers.FileField(
        required=True,
        help_text="CSV or XLSX file to upload"
    )
    
    def validate_file(self, value):
        """Validate uploaded file."""
        # Check file size (max 20MB)
        if value.size > 20 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 20MB")
        
        # Check file type
        valid_extensions = ['.csv', '.xlsx', '.xls']
        filename = value.name.lower()
        if not any(filename.endswith(ext) for ext in valid_extensions):
            raise serializers.ValidationError(
                "Invalid file type. Please upload a CSV or XLSX file."
            )
        
        return value


class ParsedRecordSerializer(serializers.ModelSerializer):
    """Serializer for ParsedRecord model."""
    
    class Meta:
        model = ParsedRecord
        fields = ['id', 'dataset', 'row_index', 'data']
        read_only_fields = ['id']
