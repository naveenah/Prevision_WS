"""
Custom JWT serializers for authentication
"""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that accepts email instead of username for login.
    
    Frontend sends: { "email": "user@example.com", "password": "..." }
    Backend authenticates using email and returns JWT tokens.
    """
    username_field = 'email'
    
    def validate(self, attrs):
        # Get email and password from request
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Try to find user by email
            try:
                user = User.objects.get(email=email)
                # Authenticate using username (Django's default)
                user = authenticate(
                    request=self.context.get('request'),
                    username=user.username,
                    password=password
                )
                
                if not user:
                    raise serializers.ValidationError(
                        'No active account found with the given credentials'
                    )
                    
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    'No active account found with the given credentials'
                )
            
            # Get tokens using parent class method
            refresh = self.get_token(user)
            
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            
            return data
        else:
            raise serializers.ValidationError(
                'Must include "email" and "password".'
            )

