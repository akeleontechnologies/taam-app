"""
URL patterns for the ingest app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UploadedDatasetViewSet

router = DefaultRouter()
router.register(r'datasets', UploadedDatasetViewSet, basename='dataset')

urlpatterns = [
    path('', include(router.urls)),
]
