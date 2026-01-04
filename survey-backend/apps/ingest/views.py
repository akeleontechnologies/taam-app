"""
Views for the ingest app - handles file uploads and dataset management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import UploadedDataset, ParsedRecord
from .serializers import (
    UploadedDatasetSerializer,
    DatasetUploadSerializer,
    ParsedRecordSerializer,
)
from .services import (
    save_uploaded_file,
    parse_uploaded_file,
    get_dataframe_profile,
    is_taam_dataset,
    dataframe_to_records,
)
from apps.commons.permissions import IsOwnerOrAdmin


class UploadedDatasetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing uploaded datasets.
    """
    serializer_class = UploadedDatasetSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'
    
    def get_queryset(self):
        """Return datasets for current user, or all if admin."""
        user = self.request.user
        if user.is_staff:
            return UploadedDataset.objects.all()
        return UploadedDataset.objects.filter(owner=user)
    
    @action(detail=False, methods=['post'], serializer_class=DatasetUploadSerializer)
    def upload(self, request):
        """
        Upload a new CSV or XLSX file.
        
        POST /api/datasets/upload/
        """
        serializer = DatasetUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uploaded_file = serializer.validated_data['file']
        user = request.user
        
        try:
            with transaction.atomic():
                # Save the file
                file_path = save_uploaded_file(uploaded_file, user.id)
                
                # Parse the file
                df, original_headers, error = parse_uploaded_file(file_path)
                
                # Create dataset record
                dataset = UploadedDataset.objects.create(
                    owner=user,
                    filename=uploaded_file.name,
                    mime_type=uploaded_file.content_type or 'application/octet-stream',
                    size_bytes=uploaded_file.size,
                    storage_path=file_path,
                    original_headers=original_headers,
                    row_count=len(df) if df is not None else 0,
                    parsed_ok=df is not None,
                    error_message=error,
                )
                
                # Optionally save records (for smaller datasets)
                # WARNING: Large datasets will bloat the database
                if df is not None and len(df) <= 5000:  # Increased from 1000
                    records = dataframe_to_records(df)
                    parsed_records = [
                        ParsedRecord(
                            dataset=dataset,
                            row_index=idx,
                            data=record
                        )
                        for idx, record in enumerate(records)
                    ]
                    ParsedRecord.objects.bulk_create(parsed_records, batch_size=500)
                
                return Response(
                    {
                        'success': True,
                        'dataset': UploadedDatasetSerializer(dataset).data,
                        'message': 'File uploaded and parsed successfully',
                    },
                    status=status.HTTP_201_CREATED
                )
                
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def profile(self, request, uid=None):
        """
        Get detailed profile of a dataset.
        
        GET /api/datasets/{uid}/profile/
        """
        dataset = self.get_object()
        
        try:
            # Re-parse file for profile
            df, _, error = parse_uploaded_file(dataset.storage_path)
            
            if error:
                return Response(
                    {'error': error},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            profile = get_dataframe_profile(df)
            
            return Response({
                'dataset': UploadedDatasetSerializer(dataset).data,
                'profile': profile,
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def records(self, request, uid=None):
        """
        Get parsed records for a dataset.
        
        GET /api/datasets/{uid}/records/
        """
        dataset = self.get_object()
        
        # Get from DB if available
        records = ParsedRecord.objects.filter(dataset=dataset).order_by('row_index')
        
        if records.exists():
            serializer = ParsedRecordSerializer(records, many=True)
            return Response({
                'count': records.count(),
                'records': serializer.data,
            })
        
        # Otherwise parse file on-the-fly
        try:
            df, _, error = parse_uploaded_file(dataset.storage_path)
            
            if error:
                return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
            
            # Limit to first 100 records for performance
            records_data = dataframe_to_records(df, max_records=100)
            
            return Response({
                'count': len(df),
                'records': records_data,
                'note': 'Showing first 100 records' if len(df) > 100 else None,
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
