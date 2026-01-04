from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class HealthCheckView(APIView):
    """Simple health check endpoint"""
    permission_classes = []
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'message': 'Django App Manager API is running'
        }, status=status.HTTP_200_OK)
