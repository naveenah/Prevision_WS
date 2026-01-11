"""
User Registration View and Serializer
"""

from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db import transaction
from tenants.models import Tenant, Domain
import re

User = get_user_model()


class UserRegistrationSerializer(serializers.Serializer):
    """Serializer for user registration"""

    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, min_length=8, required=True
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    company_name = serializers.CharField(max_length=100, required=True)

    def validate_username(self, value):
        """Check if username already exists"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate(self, data):
        """Validate that passwords match"""
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match"}
            )
        return data

    def create(self, validated_data):
        """Create user and tenant in a transaction"""
        with transaction.atomic():
            # Remove password_confirm as it's not needed for user creation
            validated_data.pop("password_confirm")
            company_name = validated_data.pop("company_name")

            # Create user
            user = User.objects.create_user(
                username=validated_data["username"],
                email=validated_data["email"],
                password=validated_data["password"],
            )

            # Create tenant for this user
            # Generate schema name from username
            schema_name = re.sub(r"[^a-zA-Z0-9_]", "_", user.username.lower())
            schema_name = f"tenant_{schema_name}"

            # Ensure schema name is unique
            counter = 1
            original_schema = schema_name
            while Tenant.objects.filter(schema_name=schema_name).exists():
                schema_name = f"{original_schema}_{counter}"
                counter += 1

            # Create tenant
            tenant = Tenant.objects.create(
                schema_name=schema_name,
                name=company_name,
                description=f"Tenant for {user.username}",
            )

            # Create domain for tenant
            # In development, use subdomain pattern: username.localhost
            # In production, this would be username.yourdomain.com
            domain_name = f"{user.username}.localhost"
            Domain.objects.create(
                domain=domain_name, tenant=tenant, is_primary=True
            )

            return {"user": user, "tenant": tenant, "domain": domain_name}


class UserRegistrationView(APIView):
    """
    API endpoint for user registration.

    POST /api/v1/auth/register/
    {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "company_name": "Acme Corp"
    }

    Returns:
    {
        "message": "User registered successfully",
        "user": {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com"
        },
        "tenant": {
            "name": "Acme Corp",
            "schema_name": "tenant_john_doe",
            "domain": "john_doe.localhost"
        },
        "tokens": {
            "refresh": "...",
            "access": "..."
        }
    }
    """

    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            result = serializer.save()
            user = result["user"]
            tenant = result["tenant"]
            domain = result["domain"]

            # Generate JWT tokens for immediate login
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "User registered successfully",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                    "tenant": {
                        "name": tenant.name,
                        "schema_name": tenant.schema_name,
                        "domain": domain,
                    },
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
