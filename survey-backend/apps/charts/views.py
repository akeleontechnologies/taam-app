"""
Views for the charts app - handles chart generation and selection.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import ChartSpec, UserSelection
from .serializers import (
    ChartSpecSerializer,
    UserSelectionSerializer,
    ChartSelectionInputSerializer,
)
from .services import generate_taam_chart_specs, generate_generic_chart_specs
from .respondent_service import get_respondent_charts_paginated
from .filter_service import get_filter_options, get_filtered_distribution
from apps.ingest.models import UploadedDataset
from apps.ingest.services import parse_uploaded_file, is_taam_dataset


class ChartSpecViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chart specifications.
    """
    serializer_class = ChartSpecSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'
    
    def get_queryset(self):
        """Return charts for current user, or all if admin."""
        user = self.request.user
        if user.is_staff:
            return ChartSpec.objects.all()
        return ChartSpec.objects.filter(owner=user)
    
    def list(self, request, *args, **kwargs):
        """Override list to add dataset filtering and limit payload."""
        dataset_uid = request.query_params.get('dataset')
        
        if dataset_uid:
            # Filter by dataset
            queryset = self.get_queryset().filter(dataset__uid=dataset_uid)
        else:
            queryset = self.get_queryset()
        
        # Order by respondent_index for TAAM charts, created_at for others
        # Use raw JSON field ordering for respondent_index
        from django.db.models import F, Value
        from django.db.models.functions import Coalesce, Cast
        from django.db.models import IntegerField
        
        queryset = queryset.annotate(
            respondent_idx=Coalesce(
                Cast(F('derived_metrics__respondent_index'), IntegerField()),
                Value(999999)
            )
        ).order_by('respondent_idx', 'created_at')
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='summary')
    def chart_summary(self, request):
        """
        Get chart count summary for all datasets.
        
        GET /api/charts/summary/
        Returns: [{"dataset_uid": "...", "chart_count": 123, "has_distribution": true}, ...]
        """
        from django.db.models import Count, Q
        
        user = request.user
        queryset = ChartSpec.objects.filter(owner=user)
        
        summary = queryset.values('dataset__uid').annotate(
            chart_count=Count('id'),
            has_distribution=Count('id', filter=Q(chart_type='persona_distribution'))
        ).order_by('-chart_count')
        
        return Response({
            'results': [
                {
                    'dataset_uid': item['dataset__uid'],
                    'chart_count': item['chart_count'],
                    'has_distribution': item['has_distribution'] > 0
                }
                for item in summary
            ]
        })
    
    @action(detail=False, methods=['get'], url_path='dataset/(?P<dataset_uid>[^/.]+)/respondents')
    def respondent_charts(self, request, dataset_uid=None):
        """
        Get respondent charts on-demand from CSV file (no database storage).
        
        GET /api/charts/dataset/{dataset_uid}/respondents/?page=1&page_size=20
        Returns paginated respondent charts generated from the CSV file.
        """
        # Get dataset
        try:
            dataset = UploadedDataset.objects.get(uid=dataset_uid, owner=request.user)
        except UploadedDataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get pagination params
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # Generate charts from CSV
        result = get_respondent_charts_paginated(
            file_path=dataset.storage_path,
            page=page,
            page_size=page_size
        )
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(result)
    
    @action(detail=False, methods=['get'], url_path='dataset/(?P<dataset_uid>[^/.]+)/filter-options')
    def filter_options(self, request, dataset_uid=None):
        """
        Get available filter options for a dataset.
        
        GET /api/charts/dataset/{dataset_uid}/filter-options/
        Returns: {age_groups: [...], genders: [...], emirates: [...]}
        """
        try:
            dataset = UploadedDataset.objects.get(uid=dataset_uid, owner=request.user)
        except UploadedDataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        options = get_filter_options(dataset.storage_path)
        return Response(options)
    
    @action(detail=False, methods=['get'], url_path='dataset/(?P<dataset_uid>[^/.]+)/filtered-distribution')
    def filtered_distribution(self, request, dataset_uid=None):
        """
        Get persona distribution with optional filters.
        
        GET /api/charts/dataset/{dataset_uid}/filtered-distribution/?age_group=26-30&gender=Female&emirate=Ras+Al-Khaimah
        Returns filtered distribution data.
        """
        try:
            dataset = UploadedDataset.objects.get(uid=dataset_uid, owner=request.user)
        except UploadedDataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get filter params
        age_group = request.query_params.get('age_group')
        gender = request.query_params.get('gender')
        emirate = request.query_params.get('emirate')
        
        result = get_filtered_distribution(
            file_path=dataset.storage_path,
            age_group=age_group,
            gender=gender,
            emirate=emirate
        )
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate charts for a dataset.
        
        POST /api/charts/generate/
        Body: {"dataset_id": "<uid>"}
        """
        dataset_uid = request.data.get('dataset_id')
        
        if not dataset_uid:
            return Response(
                {'error': 'dataset_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get dataset
        dataset = get_object_or_404(
            UploadedDataset,
            uid=dataset_uid,
            owner=request.user
        )
        
        if not dataset.parsed_ok:
            return Response(
                {'error': 'Dataset was not parsed successfully'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Parse file
                df, _, error = parse_uploaded_file(dataset.storage_path)
                
                if error:
                    return Response(
                        {'error': error},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Determine if TAAM dataset
                is_taam = is_taam_dataset(df)
                
                # Generate chart specs
                if is_taam:
                    chart_specs_data = generate_taam_chart_specs(
                        df,
                        dataset.id,
                        request.user.id
                    )
                else:
                    chart_specs_data = generate_generic_chart_specs(
                        df,
                        dataset.id,
                        request.user.id
                    )
                
                # Create ChartSpec objects using bulk_create for performance
                print(f"DEBUG: About to create {len(chart_specs_data)} charts")
                
                chart_objects = [
                    ChartSpec(
                        owner=request.user,
                        dataset=dataset,
                        chart_type=spec_data['chart_type'],
                        chart_config=spec_data['chart_config'],
                        is_canonical=spec_data['is_canonical'],
                        derived_metrics=spec_data['derived_metrics'],
                    )
                    for spec_data in chart_specs_data
                ]
                
                charts = ChartSpec.objects.bulk_create(chart_objects, batch_size=2000)
                print(f"DEBUG: Successfully created {len(charts)} charts in database")
                
                # Don't serialize all charts in response - it's too big
                # Just return the count and success message
                return Response({
                    'success': True,
                    'is_taam': is_taam,
                    'charts_created': len(charts),
                    'message': f'Successfully generated {len(charts)} charts',
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"ERROR generating charts: {str(e)}")
            print(f"Traceback:\n{error_trace}")
            return Response(
                {'error': str(e), 'traceback': error_trace},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def select(self, request, uid=None):
        """
        Select a chart as the user's preferred chart for this dataset.
        
        POST /api/charts/{uid}/select/
        Body: {"note": "optional note"}
        """
        chart = self.get_object()
        serializer = ChartSelectionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Create or update user selection
            selection, created = UserSelection.objects.update_or_create(
                user=request.user,
                dataset=chart.dataset,
                defaults={
                    'selected_chart': chart,
                    'note': serializer.validated_data.get('note', ''),
                }
            )
            
            return Response({
                'success': True,
                'created': created,
                'selection': UserSelectionSerializer(selection).data,
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserSelectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user chart selections.
    """
    serializer_class = UserSelectionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'
    
    def get_queryset(self):
        """Return selections for current user, or all if admin."""
        user = self.request.user
        if user.is_staff:
            return UserSelection.objects.all()
        return UserSelection.objects.filter(user=user)
