# Test Implementation Plan - AI Brand Automator

## Overview

This document provides a step-by-step implementation plan for comprehensive testing of all DRF microservices. We'll start with the **Onboarding Service** as a reference implementation, then systematically apply the same patterns to other services.

---

## Phase 1: Setup & Infrastructure (Est: 2-3 hours)

### Task 1.1: Install Additional Dependencies
**File**: `ai-brand-automator/requirements-dev.txt`

```bash
# Add Hypothesis for property-based testing
hypothesis==6.92.0
hypothesis[django]==6.92.0
```

**Action**:
```bash
cd ai-brand-automator
source ../.venv/bin/activate
pip install hypothesis hypothesis[django]
pip freeze | grep hypothesis >> requirements-dev.txt
```

---

### Task 1.2: Configure Pytest
**File**: `ai-brand-automator/pytest.ini`

```ini
[pytest]
DJANGO_SETTINGS_MODULE = brand_automator.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Test markers
markers =
    unit: Unit tests (fast, isolated components)
    integration: Integration tests (multiple components)
    hypothesis: Property-based tests with Hypothesis
    slow: Slow tests (skip during rapid development)
    skip_ci: Skip in CI environment
    django_db: Tests requiring database access

# Coverage settings
addopts =
    --strict-markers
    --tb=short
    --disable-warnings
    --hypothesis-show-statistics
    --hypothesis-seed=0

# Hypothesis settings
[hypothesis]
max_examples = 100
deadline = 500
derandomize = true
```

---

### Task 1.3: Create Global Fixtures
**File**: `ai-brand-automator/conftest.py`

```python
"""
Global pytest fixtures and configuration
"""
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from hypothesis import settings

User = get_user_model()

# Hypothesis profile for faster local development
settings.register_profile("ci", max_examples=200, deadline=1000)
settings.register_profile("dev", max_examples=50, deadline=500)
settings.load_profile("dev")


@pytest.fixture
def api_client():
    """DRF API test client"""
    return APIClient()


@pytest.fixture
def user(db):
    """Create test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """API client authenticated with test user"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def tenant(db):
    """Create test tenant with domain"""
    from tenants.models import Tenant, Domain
    
    tenant = Tenant.objects.create(
        name='Test Company',
        schema_name='tenant_test',
        subscription_status='active'
    )
    Domain.objects.create(
        tenant=tenant,
        domain='test.localhost',
        is_primary=True
    )
    return tenant


@pytest.fixture
def mock_gemini_api(mocker):
    """Mock Gemini AI API responses"""
    mock_response = {
        'vision_statement': 'To revolutionize the industry',
        'mission_statement': 'We deliver exceptional value',
        'values': ['Innovation', 'Excellence', 'Integrity'],
        'positioning_statement': 'The leader in innovative solutions',
    }
    return mocker.patch(
        'ai_services.services.GeminiAIService.generate_brand_strategy',
        return_value=mock_response
    )


@pytest.fixture
def mock_gcs_upload(mocker):
    """Mock Google Cloud Storage uploads"""
    return mocker.patch(
        'files.services.GCSService.upload_file',
        return_value='https://storage.googleapis.com/test-bucket/test-file.jpg'
    )


@pytest.fixture(autouse=True)
def mock_email_backend(settings):
    """Auto-mock email backend for all tests"""
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


@pytest.fixture
def mock_request_tenant(mocker, tenant):
    """Mock request.tenant attribute"""
    def _mock_request(request):
        request.tenant = tenant
        return request
    return _mock_request
```

---

## Phase 2: Onboarding Service Tests (Est: 8-10 hours)

### Task 2.1: Create Test Directory Structure
```bash
mkdir -p ai-brand-automator/onboarding/tests
touch ai-brand-automator/onboarding/tests/__init__.py
touch ai-brand-automator/onboarding/tests/factories.py
touch ai-brand-automator/onboarding/tests/test_models.py
touch ai-brand-automator/onboarding/tests/test_serializers.py
touch ai-brand-automator/onboarding/tests/test_views.py
touch ai-brand-automator/onboarding/tests/test_integration.py
touch ai-brand-automator/onboarding/tests/test_properties.py
```

---

### Task 2.2: Create Factories
**File**: `ai-brand-automator/onboarding/tests/factories.py`

```python
"""
Factory Boy factories for onboarding models
"""
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from onboarding.models import Company, BrandAsset, OnboardingProgress

fake = Faker()


class CompanyFactory(DjangoModelFactory):
    """Factory for Company model"""
    
    class Meta:
        model = Company
    
    name = factory.Faker('company')
    description = factory.Faker('paragraph', nb_sentences=3)
    industry = factory.Faker('random_element', elements=[
        'Technology', 'Healthcare', 'Finance', 'E-commerce', 'Manufacturing'
    ])
    target_audience = factory.Faker('paragraph', nb_sentences=2)
    core_problem = factory.Faker('sentence')
    brand_voice = factory.Faker('random_element', elements=[
        'professional', 'friendly', 'bold', 'authoritative'
    ])
    
    # AI-generated fields (optional)
    vision_statement = factory.Faker('sentence')
    mission_statement = factory.Faker('sentence')
    values = factory.LazyFunction(lambda: ['Innovation', 'Excellence', 'Integrity'])
    
    # tenant must be provided explicitly
    tenant = None


class BrandAssetFactory(DjangoModelFactory):
    """Factory for BrandAsset model"""
    
    class Meta:
        model = BrandAsset
    
    file_name = factory.Faker('file_name', extension='jpg')
    file_type = 'image'
    file_url = factory.LazyAttribute(
        lambda obj: f'https://storage.googleapis.com/test/{obj.file_name}'
    )
    file_size = factory.Faker('random_int', min=1024, max=5242880)  # 1KB to 5MB
    mime_type = 'image/jpeg'
    
    # tenant and company must be provided
    tenant = None
    company = None


class OnboardingProgressFactory(DjangoModelFactory):
    """Factory for OnboardingProgress model"""
    
    class Meta:
        model = OnboardingProgress
    
    current_step = 'company_info'
    completed_steps = factory.LazyFunction(list)
    
    # Metadata
    company_info_completed = False
    assets_uploaded = False
    brand_strategy_generated = False
    brand_identity_generated = False
    
    # tenant must be provided
    tenant = None
```

---

### Task 2.3: Model Tests
**File**: `ai-brand-automator/onboarding/tests/test_models.py`

**Status**: Ready to implement  
**Lines of Code**: ~150  
**Est. Time**: 1.5 hours

**Test Coverage**:
- Company model creation
- Field validation (required, max_length, choices)
- Default values (JSONField)
- Relationship integrity (OneToOne with Tenant)
- String representation
- Model constraints

**Sample Test Structure**:
```python
import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from onboarding.models import Company, BrandAsset
from onboarding.tests.factories import CompanyFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestCompanyModel:
    """Test Company model"""
    
    def test_create_company_with_valid_data(self, tenant):
        """Test creating company with all required fields"""
        company = CompanyFactory(tenant=tenant, name='Acme Corp')
        assert company.pk is not None
        assert company.name == 'Acme Corp'
        assert company.tenant == tenant
    
    def test_company_requires_tenant(self):
        """Test company creation fails without tenant"""
        with pytest.raises(IntegrityError):
            CompanyFactory(tenant=None)
    
    def test_company_str_representation(self, tenant):
        """Test __str__ method"""
        company = CompanyFactory(tenant=tenant, name='Test Co')
        assert 'Test Co' in str(company)
    
    def test_values_field_defaults_to_empty_list(self, tenant):
        """Test JSONField default value"""
        company = CompanyFactory(tenant=tenant)
        assert isinstance(company.values, list)
    
    def test_brand_voice_choices_validation(self, tenant):
        """Test brand_voice field accepts valid choices"""
        valid_choices = ['professional', 'friendly', 'bold']
        for choice in valid_choices:
            company = CompanyFactory(tenant=tenant, brand_voice=choice)
            company.full_clean()  # Should not raise
    
    # Add ~10 more test methods...
```

---

### Task 2.4: Serializer Tests
**File**: `ai-brand-automator/onboarding/tests/test_serializers.py`

**Status**: Ready to implement  
**Lines of Code**: ~200  
**Est. Time**: 2 hours

**Test Coverage**:
- Serialization (model → dict)
- Deserialization (dict → model)
- Validation (required fields, field types)
- Read-only fields
- Nested serialization
- Error messages

---

### Task 2.5: ViewSet Tests
**File**: `ai-brand-automator/onboarding/tests/test_views.py`

**Status**: Ready to implement  
**Lines of Code**: ~300  
**Est. Time**: 3 hours

**Test Coverage**:
- List endpoint (GET /api/v1/companies/)
- Create endpoint (POST with auth)
- Retrieve single (GET /api/v1/companies/{id}/)
- Update (PUT/PATCH)
- Delete (DELETE)
- Permissions (IsAuthenticated)
- Tenant filtering
- Custom actions (generate_brand_strategy)

---

### Task 2.6: Integration Tests
**File**: `ai-brand-automator/onboarding/tests/test_integration.py`

**Status**: Ready to implement  
**Lines of Code**: ~150  
**Est. Time**: 1.5 hours

**Test Coverage**:
- Complete onboarding flow
- Multi-tenant isolation
- Error handling
- Pagination

---

### Task 2.7: Property Tests
**File**: `ai-brand-automator/onboarding/tests/test_properties.py`

**Status**: Ready to implement  
**Lines of Code**: ~100  
**Est. Time**: 1 hour

**Test Coverage**:
- Random company data generation
- Serializer round-trip property
- Edge cases discovery

---

## Phase 3: AI Services Tests (Est: 6-8 hours)

### Task 3.1: Create Test Structure
```bash
mkdir -p ai-brand-automator/ai_services/tests
# Create test files similar to onboarding
```

### Task 3.2-3.7: Implement Tests
- factories.py (ChatSession, AIGeneration)
- test_models.py
- test_serializers.py
- test_views.py
- test_services.py (AI service mocking)
- test_properties.py

**Key Focus**: Mock external AI API calls, test fallback behavior

---

## Phase 4: Authentication Tests (Est: 4-5 hours)

### Task 4.1: Create Test Structure
```bash
mkdir -p ai-brand-automator/brand_automator/tests
```

### Task 4.2-4.5: Implement Tests
- test_auth_views.py (registration, login, JWT)
- test_validators.py (password strength, file validation)
- test_middleware.py (security headers, tenant resolution)
- test_health_views.py (health checks)

---

## Phase 5: Tenants Tests (Est: 3-4 hours)

### Task 5.1: Enhance Existing Tests
**File**: Update `ai-brand-automator/tenants/tests/test_tenant_models.py`

### Task 5.2: Add Multi-Tenancy Tests
- Tenant schema creation
- Domain routing
- Data isolation verification
- Cross-tenant access prevention

---

## Phase 6: Files & Automation Services (Est: 4-5 hours)

### Task 6.1-6.2: Files Service
- GCS upload mocking
- File validation tests
- Asset management tests

### Task 6.3-6.4: Automation Service
- Model tests
- ViewSet tests (if implemented)

---

## Phase 7: Cross-Service Integration (Est: 3-4 hours)

### Task 7.1: End-to-End Workflows
**File**: `ai-brand-automator/tests/test_e2e.py`

**Test Scenarios**:
1. User Registration → Company Creation → AI Generation
2. File Upload → Brand Asset Creation → AI Analysis
3. Multi-tenant data isolation verification
4. Complete onboarding flow

---

## Phase 8: Property-Based Testing Enhancement (Est: 3-4 hours)

### Task 8.1: Comprehensive Hypothesis Strategies
- Create custom strategies for all models
- Discover edge cases in serializers
- Test invariants across services

---

## Implementation Schedule

### Week 1
- **Days 1-2**: Phase 1 (Setup) + Phase 2.1-2.3 (Onboarding Models/Factories)
- **Days 3-5**: Phase 2.4-2.7 (Onboarding Serializers/Views/Integration)

### Week 2
- **Days 1-3**: Phase 3 (AI Services)
- **Days 4-5**: Phase 4 (Authentication)

### Week 3
- **Days 1-2**: Phase 5 (Tenants)
- **Days 3-4**: Phase 6 (Files/Automation)
- **Day 5**: Phase 7 (E2E Integration)

### Week 4
- **Days 1-2**: Phase 8 (Property Tests Enhancement)
- **Days 3-4**: Bug fixes, refactoring, documentation
- **Day 5**: Final review, coverage report, team demo

---

## Success Criteria

✅ **Phase 1**: pytest configuration working, global fixtures functional  
✅ **Phase 2**: Onboarding service 85%+ coverage, all tests passing  
✅ **Phase 3**: AI services 80%+ coverage, mocking working  
✅ **Phase 4**: Authentication 90%+ coverage (critical path)  
✅ **Phase 5**: Tenant isolation verified  
✅ **Phase 6**: File/Automation services covered  
✅ **Phase 7**: E2E workflows validated  
✅ **Phase 8**: Hypothesis discovers ≥5 new edge cases  

**Overall Target**: 80%+ code coverage, <30s test execution time

---

## Risk Mitigation

### Potential Blockers
1. **Multi-tenancy complexity** - Mock tenant middleware carefully
2. **AI API costs** - Ensure all AI calls are mocked
3. **GCS authentication** - Mock storage service
4. **Database schema issues** - Use pytest-django transactions

### Solutions
- Start with unit tests (no external dependencies)
- Create comprehensive fixtures in conftest.py
- Document mocking patterns for team
- Use CI to catch regressions early

---

## Next Actions

1. **Approve this plan** - Team review and sign-off
2. **Create tracking board** - GitHub project or Jira
3. **Start Phase 1** - Install dependencies, configure pytest
4. **Implement Phase 2.1-2.3** - Onboarding factories and model tests
5. **Daily standups** - Track progress, unblock issues

---

**Ready to start implementation!** 🚀

Would you like me to begin with Phase 1 (Setup) or jump directly into implementing the Onboarding service tests?
