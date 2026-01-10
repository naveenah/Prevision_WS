"""
URL configuration for brand_automator project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from onboarding.auth_serializers import EmailTokenObtainPairSerializer
from onboarding.registration import UserRegistrationView


class EmailTokenObtainPairView(TokenObtainPairView):
    """Custom view that uses email-based authentication"""
    serializer_class = EmailTokenObtainPairSerializer


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        # Authentication - now accepts email instead of username
        path('auth/register/', UserRegistrationView.as_view(), name='user_register'),
        path('auth/login/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

        # Onboarding
        path('', include('onboarding.urls')),

        # AI Services
        path('ai/', include('ai_services.urls')),
    ])),
]
