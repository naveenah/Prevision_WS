from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, BrandAssetViewSet, OnboardingProgressViewSet

router = DefaultRouter()
router.register(r"companies", CompanyViewSet)
router.register(r"assets", BrandAssetViewSet)
router.register(r"progress", OnboardingProgressViewSet)

urlpatterns = router.urls
