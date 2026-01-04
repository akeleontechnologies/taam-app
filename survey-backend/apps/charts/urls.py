"""
URL patterns for the charts app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChartSpecViewSet, UserSelectionViewSet

router = DefaultRouter()
router.register(r'charts', ChartSpecViewSet, basename='chart')
router.register(r'selections', UserSelectionViewSet, basename='selection')

urlpatterns = [
    path('', include(router.urls)),
]
