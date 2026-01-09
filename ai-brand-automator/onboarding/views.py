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


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for Company model"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # For now, return all companies (will be filtered by tenant in multi-tenant setup)
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

        # TODO: Integrate with AI service
        # For now, return mock response
        company.vision_statement = f"Our vision is to revolutionize the {company.industry} industry through innovative solutions."
        company.mission_statement = f"To provide exceptional {company.industry} services that solve {company.core_problem} for our customers."
        company.values = ["Innovation", "Customer Focus", "Excellence", "Integrity"]
        company.positioning_statement = f"The leading {company.industry} solution for businesses seeking to overcome {company.core_problem}."
        company.save()

        serializer = self.get_serializer(company)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def generate_brand_identity(self, request, pk=None):
        """Generate AI-powered brand identity"""
        company = self.get_object()

        # TODO: Integrate with AI service
        # For now, return mock response
        company.color_palette_desc = "Primary: Deep Blue (#1a365d), Secondary: Teal (#319795), Accent: Orange (#ed8936)"
        company.font_recommendations = "Primary: Inter (Sans-serif), Secondary: Playfair Display (Serif)"
        company.messaging_guide = "Professional yet approachable tone. Focus on innovation and customer success."
        company.save()

        serializer = self.get_serializer(company)
        return Response(serializer.data)


class BrandAssetViewSet(viewsets.ModelViewSet):
    """ViewSet for BrandAsset model"""
    queryset = BrandAsset.objects.all()
    serializer_class = BrandAssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # For now, return all assets (will be filtered by tenant in multi-tenant setup)
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

        # TODO: Upload to Google Cloud Storage
        # For now, store locally
        gcs_path = f"assets/{tenant.id}/{file.name}"

        # Create asset record
        asset = BrandAsset.objects.create(
            tenant=tenant,
            company=company,
            file_name=file.name,
            file_type=file_type,
            file_size=file.size,
            gcs_path=gcs_path,
            processed=True  # Mark as processed for now
        )

        response_serializer = BrandAssetSerializer(asset)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class OnboardingProgressViewSet(viewsets.ModelViewSet):
    """ViewSet for OnboardingProgress model"""
    queryset = OnboardingProgress.objects.all()
    serializer_class = OnboardingProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # For now, return all progress records (will be filtered by tenant in multi-tenant setup)
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
