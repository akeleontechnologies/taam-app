from django.test import TestCase
from django.contrib.auth.hashers import check_password
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User


class UserModelTest(TestCase):
    """Test cases for User model."""
    
    def test_create_user(self):
        """Test creating a user with valid data."""
        user = User.objects.create(
            email='test@example.com',
            firstname='John',
            lastname='Doe',
            password='testpassword123'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.firstname, 'John')
        self.assertEqual(user.lastname, 'Doe')
        self.assertTrue(check_password('testpassword123', user.password))
    
    def test_user_full_name(self):
        """Test full_name property."""
        user = User.objects.create(
            email='test@example.com',
            firstname='John',
            lastname='Doe',
            password='testpassword123'
        )
        
        self.assertEqual(user.full_name, 'John Doe')


class UserAPITest(APITestCase):
    """Test cases for User API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'email': 'newuser@example.com',
            'firstname': 'Jane',
            'lastname': 'Smith',
            'password': 'securepassword123',
            'password_confirm': 'securepassword123'
        }
    
    def test_create_user(self):
        """Test creating a user via API."""
        response = self.client.post('/api/users/', self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'newuser@example.com')
    
    def test_create_user_password_mismatch(self):
        """Test creating a user with mismatched passwords."""
        self.user_data['password_confirm'] = 'differentpassword'
        response = self.client.post('/api/users/', self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
