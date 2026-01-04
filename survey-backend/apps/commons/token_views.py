from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .authentication import ExpiringTokenAuthentication


@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_auth_token(request):
    """
    Obtain authentication token
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if email and password:
        user = authenticate(email=email, password=password)
        if user:
            if user.is_active:
                token, created = Token.objects.get_or_create(user=user)
                
                # Check if token is expired and create new one if needed
                is_expired, token = ExpiringTokenAuthentication.validate_token_expiration(token)
                if is_expired:
                    token = Token.objects.create(user=user)
                
                return Response({
                    'token': token.key,
                    'user_id': user.id,
                    'email': user.email,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'is_staff': user.is_staff,
                    'expires_in': ExpiringTokenAuthentication.expires_in(token).total_seconds()
                })
            else:
                return Response(
                    {'error': 'User account is disabled.'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(
                {'error': 'Invalid email or password.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    else:
        return Response(
            {'error': 'Email and password are required.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def logout(request):
    """
    Logout user by deleting token
    """
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out.'})
    except:
        return Response(
            {'error': 'No active session found.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def token_status(request):
    """
    Check token status and expiration
    """
    try:
        token = Token.objects.get(user=request.user)
        is_expired = ExpiringTokenAuthentication.is_expired(token)
        expires_in = ExpiringTokenAuthentication.expires_in(token)
        
        return Response({
            'is_expired': is_expired,
            'expires_in_seconds': expires_in.total_seconds() if not is_expired else 0,
            'email': request.user.email,
            'firstname': request.user.firstname,
            'lastname': request.user.lastname,
        })
    except Token.DoesNotExist:
        return Response(
            {'error': 'No token found for user.'}, 
            status=status.HTTP_404_NOT_FOUND
        )
