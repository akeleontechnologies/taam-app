from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from apps.commons.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for reading User data.
    Excludes password from responses.
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'firstname', 'lastname', 'full_name', 'is_active', 'is_staff', 'created', 'modified']
        read_only_fields = ['id', 'created', 'modified']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users.
    Includes password field with write-only access.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm your password"
    )
    
    class Meta:
        model = User
        fields = ['id', 'email', 'firstname', 'lastname', 'password', 'password_confirm', 'is_active']
        read_only_fields = ['id']
        extra_kwargs = {
            'email': {'required': True},
            'firstname': {'required': True},
            'lastname': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate that passwords match."""
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)
        
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        
        return attrs
    
    def validate_email(self, value):
        """Validate email is unique."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value.lower()
    
    def create(self, validated_data):
        """Create user with hashed password."""
        # Password will be automatically hashed in the model's save method
        return User.objects.create(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user data.
    Allows partial updates and excludes password changes (use separate endpoint for that).
    """
    class Meta:
        model = User
        fields = ['email', 'firstname', 'lastname', 'is_active']
        extra_kwargs = {
            'email': {'required': False},
            'firstname': {'required': False},
            'lastname': {'required': False},
        }
    
    def validate_email(self, value):
        """Validate email is unique if changed."""
        user = self.instance
        if User.objects.filter(email__iexact=value).exclude(id=user.id).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value.lower()


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate passwords."""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'New passwords do not match.'
            })
        
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password is correct."""
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError('Old password is incorrect.')
        return value
