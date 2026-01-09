from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Company, BrandAsset, OnboardingProgress
from .serializers import (
    CompanySerializer, BrandAssetSerializer, OnboardingProgressSerializer,
    CompanyCreateSerializer, CompanyUpdateSerializer, BrandAssetUploadSerializer
)
from files.services import gcs_service
from ai_services.services import ai_service


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for Company model"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter by tenant in multi-tenant setup
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Company.objects.filter(tenant=self.request.tenant)
        return Company.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CompanyCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CompanyUpdateSerializer
        return CompanySerializer

    def perform_create(self, serializer):
        # Create onboarding progress when company is created
        company = serializer.save()
        OnboardingProgress.objects.create(
            tenant=company.tenant,
            company=company,
            current_step='company_info',
            completed_steps=['company_info']
        )

    @action(detail=True, methods=['post'])
    def generate_brand_strategy(self, request, pk=None):
        """Generate AI-powered brand strategy"""
        company = self.get_object()

        # Prepare company data for AI service
        company_data = {
            'tenant': company.tenant,
            'name': company.name,
            'industry': company.industry,
            'target_audience': company.target_audience,
            'core_problem': company.core_problem,
            'brand_voice': company.brand_voice,
        }

        # Generate brand strategy using AI
        ai_result = ai_service.generate_brand_strategy(company_data)

        # Update company with AI-generated content
        company.vision_statement = ai_result['vision_statement']
        company.mission_statement = ai_result['mission_statement']
        company.values = ai_result['values']
        company.positioning_statement = ai_result['positioning_statement']
        company.save()

        serializer = self.get_serializer(company)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def generate_brand_identity(self, request, pk=None):
        """Generate AI-powered brand identity"""
        company = self.get_object()

        # Prepare company data for AI service
        company_data = {
            'tenant': company.tenant,
            'name': company.name,
            'industry': company.industry,
            'brand_voice': company.brand_voice,
            'target_audience': company.target_audience,
        }

        # Generate brand identity using AI
        ai_result = ai_service.generate_brand_identity(company_data)

        # Update company with AI-generated content
        company.color_palette_desc = ai_result['color_palette_desc']
        company.font_recommendations = ai_result['font_recommendations']
        company.messaging_guide = ai_result['messaging_guide']
        company.save()

        serializer = self.get_serializer(company)
        return Response(serializer.data)


class BrandAssetViewSet(viewsets.ModelViewSet):
    """ViewSet for BrandAsset model"""
    queryset = BrandAsset.objects.all()
    serializer_class = BrandAssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter by tenant in multi-tenant setup
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return BrandAsset.objects.filter(tenant=self.request.tenant)
        return BrandAsset.objects.all()

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload a brand asset file"""
        serializer = BrandAssetUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data['file']
        file_type = serializer.validated_data['file_type']

        # Get or create company for the tenant
        # TODO: Get actual tenant from request in multi-tenant setup
        tenant = request.tenant  # This will be set by middleware in multi-tenant setup
        company = get_object_or_404(Company, tenant=tenant)

        # Upload to Google Cloud Storage
        gcs_path = f"assets/{tenant.id}/{file.name}"
        try:
            public_url = gcs_service.upload_file(file, gcs_path, file.content_type)
        except Exception as e:
            return Response(
                {'error': f'File upload failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Create asset record
        asset = BrandAsset.objects.create(
            tenant=tenant,
            company=company,
            file_name=file.name,
            file_type=file_type,
            file_size=file.size,
            gcs_path=gcs_path,
            processed=True
        )

        response_serializer = BrandAssetSerializer(asset)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class OnboardingProgressViewSet(viewsets.ModelViewSet):
    """ViewSet for OnboardingProgress model"""
    queryset = OnboardingProgress.objects.all()
    serializer_class = OnboardingProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter by tenant in multi-tenant setup
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return OnboardingProgress.objects.filter(tenant=self.request.tenant)
        return OnboardingProgress.objects.all()

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current onboarding progress for the tenant"""
        # TODO: Get actual tenant from request in multi-tenant setup
        tenant = request.tenant
        progress = get_object_or_404(OnboardingProgress, tenant=tenant)
        serializer = self.get_serializer(progress)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_step(self, request):
        """Update current onboarding step"""
        step = request.data.get('step')
        completed = request.data.get('completed', False)

        if not step:
            return Response({'error': 'Step is required'}, status=status.HTTP_400_BAD_REQUEST)

        # TODO: Get actual tenant from request in multi-tenant setup
        tenant = request.tenant
        progress = get_object_or_404(OnboardingProgress, tenant=tenant)

        progress.current_step = step
        if completed and step not in progress.completed_steps:
            progress.completed_steps.append(step)

        if step == 'review':  # Final step
            progress.is_completed = True
            progress.completed_at = timezone.now()

        progress.save()

        serializer = self.get_serializer(progress)
        return Response(serializer.data)
