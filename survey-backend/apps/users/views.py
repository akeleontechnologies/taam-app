from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth.hashers import make_password
from django.db import models
from django.db.models import Count
from apps.commons.models import User
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations.
    
    Provides:
    - list: GET /api/users/ - List all users
    - create: POST /api/users/ - Create a new user
    - retrieve: GET /api/users/{id}/ - Get a specific user
    - update: PUT /api/users/{id}/ - Update a user (full update)
    - partial_update: PATCH /api/users/{id}/ - Update a user (partial update)
    - destroy: DELETE /api/users/{id}/ - Delete a user
    - change_password: POST /api/users/{id}/change_password/ - Change user password
    """
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        Set permissions based on action.
        Anyone can create an account, but other actions require authentication.
        """
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """
        Create a new user.
        POST /api/users/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return user data without password
        output_serializer = UserSerializer(user)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """
        Update a user (full update).
        PUT /api/users/{id}/
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return updated user data
        output_serializer = UserSerializer(user)
        return Response(output_serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Update a user (partial update).
        PATCH /api/users/{id}/
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a user.
        DELETE /api/users/{id}/
        """
        instance = self.get_object()
        instance.delete()
        return Response(
            {'message': 'User deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['post'], url_path='change-password')
    def change_password(self, request, pk=None):
        """
        Change user password.
        POST /api/users/{id}/change-password/
        
        Body:
        {
            "old_password": "current_password",
            "new_password": "new_password",
            "new_password_confirm": "new_password"
        }
        """
        user = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Update password
        user.password = make_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], url_path='active')
    def active_users(self, request):
        """
        Get all active users.
        GET /api/users/active/
        """
        active_users = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Search users by email, firstname, or lastname.
        GET /api/users/search/?q=search_term
        """
        search_term = request.query_params.get('q', '')
        
        if not search_term:
            return Response(
                {'error': 'Please provide a search term using the "q" parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = self.queryset.filter(
            models.Q(email__icontains=search_term) |
            models.Q(firstname__icontains=search_term) |
            models.Q(lastname__icontains=search_term)
        )
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='admin/list', permission_classes=[IsAdminUser])
    def admin_list(self, request):
        """
        Get all users with dataset and chart counts (admin only).
        GET /api/users/admin/list/
        """
        users = User.objects.annotate(
            dataset_count=Count('uploaded_datasets'),
            chart_count=Count('chart_specs'),
        ).values(
            'id',
            'email',
            'firstname',
            'lastname',
            'is_active',
            'is_staff',
            'created',
            'dataset_count',
            'chart_count',
        )
        
        # Add full_name to each user
        user_list = []
        for user in users:
            firstname = user.get('firstname') or ''
            lastname = user.get('lastname') or ''
            full_name = f"{firstname} {lastname}".strip()
            user['full_name'] = full_name if full_name else user.get('email', '')
            user_list.append(user)
        
        return Response(user_list)
    
    @action(detail=True, methods=['get'], url_path='datasets', permission_classes=[IsAuthenticated])
    def user_datasets(self, request, pk=None):
        """
        Get all datasets for a specific user.
        GET /api/users/{id}/datasets/
        Admin can view any user's datasets, regular users can only view their own.
        """
        user = self.get_object()
        
        # Check permission: admin or self
        if not request.user.is_staff and request.user.id != user.id:
            return Response(
                {'error': 'You do not have permission to view this user\'s datasets'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from apps.ingest.models import UploadedDataset
        from apps.ingest.serializers import UploadedDatasetSerializer
        
        datasets = UploadedDataset.objects.filter(owner=user).order_by('-created_at')
        serializer = UploadedDatasetSerializer(datasets, many=True)
        
        return Response({
            'user': UserSerializer(user).data,
            'datasets': serializer.data,
        })
    
    @action(detail=True, methods=['get'], url_path='charts', permission_classes=[IsAuthenticated])
    def user_charts(self, request, pk=None):
        """
        Get all charts for a specific user.
        GET /api/users/{id}/charts/
        Admin can view any user's charts, regular users can only view their own.
        """
        user = self.get_object()
        
        # Check permission: admin or self
        if not request.user.is_staff and request.user.id != user.id:
            return Response(
                {'error': 'You do not have permission to view this user\'s charts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from apps.charts.models import ChartSpec
        from apps.charts.serializers import ChartSpecSerializer
        
        charts = ChartSpec.objects.filter(owner=user).order_by('-created_at')
        serializer = ChartSpecSerializer(charts, many=True)
        
        return Response({
            'user': UserSerializer(user).data,
            'charts': serializer.data,
        })
