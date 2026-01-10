# AI Brand Automator - Copilot Instructions

## Project Overview

**Multi-tenant SaaS platform** for AI-powered brand building combining Django REST API with Next.js frontend:
- **Backend**: Django 4.2 + DRF at `ai-brand-automator/` (port 8000)
- **Frontend**: Next.js 16 + React 19 + TypeScript at `ai-brand-automator-frontend/` (port 3000)
- **Database**: PostgreSQL (Neon hosted) with schema-based multi-tenancy via `django-tenants`
- **AI**: Google Gemini 1.5 Flash via `google-generativeai` for brand strategy generation

**⚠️ CRITICAL**: Multi-tenancy is **ENABLED** but **PARTIALLY BROKEN**. The middleware is active (`TenantMainMiddleware` in MIDDLEWARE list) but SHARED_APPS/TENANT_APPS split is configured. Every request expects `request.tenant` to exist. See Multi-Tenancy section for handling strategies.

## Key Architecture Decisions

### Django Apps Structure
- `onboarding/`: Company creation → Brand strategy generation → Asset uploads (TENANT_APPS)
- `ai_services/`: Chat sessions + AI content generation (SHARED_APPS for logging)
- `tenants/`: Multi-tenant models (Tenant, Domain) - SHARED_APPS
- `files/`: GCS upload service (TENANT_APPS, not fully implemented)
- `automation/`: Placeholder for Celery background tasks (TENANT_APPS)

**Why this split?** 
- SHARED_APPS: Available in public schema + all tenants (authentication, tenant management, AI logging)
- TENANT_APPS: Isolated per-tenant data (companies, files, automation configs)

### Critical Data Flow
1. User creates `Company` via `POST /api/v1/companies/`
2. `OnboardingProgress` auto-created with `current_step='company_info'`
3. Frontend calls `POST /api/v1/companies/{id}/generate_brand_strategy/`
4. `GeminiAIService.generate_brand_strategy()` generates vision/mission/values/positioning
5. AI responses saved to Company model + `AIGeneration` logging model

**Gotcha**: Company model has `OneToOneField(Tenant)` - creation fails without valid tenant context.

### API Authentication
- JWT via `djangorestframework-simplejwt` with Bearer tokens
- Frontend stores tokens in localStorage (`access_token`, `refresh_token`)
- All API endpoints under `/api/v1/` require authentication except `/auth/login|refresh/`
- CORS configured for `localhost:3000` in development

## Development Workflows

### Running Services
```bash
# Backend (Django) - REQUIRED ORDER
cd ai-brand-automator
source ../.venv/bin/activate  # Virtual env is ONE LEVEL UP in workspace root
python manage.py runserver     # Starts on http://localhost:8000

# Frontend (Next.js) - In separate terminal
cd ai-brand-automator-frontend
npm run dev                    # Starts on http://localhost:3000
```

**⚠️ Critical**: Virtual environment is at `/Users/naveenhanuman/Documents/Workspace/git-ws/Prevision_WS/.venv`, NOT inside ai-brand-automator/

### Database Operations
```bash
# Standard Django (NOT schema-per-tenant migrations due to broken config)
python manage.py makemigrations
python manage.py migrate        # Applies to default database only

# When multi-tenancy is properly enabled, use:
# python manage.py migrate_schemas --shared  # For SHARED_APPS
# python manage.py migrate_schemas           # For all tenant schemas
```

**Current State**: Database is Neon PostgreSQL but multi-tenancy NOT functional, so migrations behave like standard Django.

### Environment Configuration
```bash
# Required .env variables (at ai-brand-automator/.env):
SECRET_KEY=<generate-with-django>
DEBUG=True
GOOGLE_API_KEY=<your-gemini-api-key>
DATABASE_URL=postgresql://...  # Optional if using hardcoded settings

# Frontend .env.local:
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Security Issue**: Database credentials currently hardcoded in settings.py (lines 103-109) - should migrate to .env

## Project-Specific Patterns

### Django ViewSets & Custom Actions
Use `@action(detail=True, methods=['post'])` for AI generation endpoints:
```python
# Pattern in onboarding/views.py
@action(detail=True, methods=['post'])
def generate_brand_strategy(self, request, pk=None):
    company = self.get_object()
    ai_result = ai_service.generate_brand_strategy(company_data)
    company.vision_statement = ai_result['vision_statement']
    company.save()
```

### AI Service Integration
- `ai_services/services.py` exports singleton `ai_service = GeminiAIService()`
- Always logs generations to `AIGeneration` model with tokens/processing time
- Fallback responses if `GOOGLE_API_KEY` not configured (mock data)
- Response parsing extracts sections like "Vision Statement", "Mission Statement" from AI text

### Frontend API Client
- Centralized in `src/lib/api.ts` with auto token injection
- Auto-redirects to `/auth/login` on 401 responses
- Always use `apiClient.get|post|put()` instead of raw fetch

### Model Conventions
- Use `timezone.now()` for created_at defaults (never `auto_now_add` for flexibility)
- JSONField for arrays/objects (e.g., `Company.values` stores list of core values)
- Help text on all model fields for admin/API documentation
- Multi-tenant models reference `tenant` field (foreign key to Tenant model when enabled)

## Important File Locations

- **Settings**: [ai-brand-automator/brand_automator/settings.py](ai-brand-automator/brand_automator/settings.py#L37-L56) - Multi-tenancy toggle
- **URL Routing**: [ai-brand-automator/brand_automator/urls.py](ai-brand-automator/brand_automator/urls.py) - API v1 prefix pattern
- **AI Service**: [ai-brand-automator/ai_services/services.py](ai-brand-automator/ai_services/services.py) - Gemini integration with fallbacks
- **Architecture Doc**: [ai_brand_automator_mvp_architecture.md](ai_brand_automator_mvp_architecture.md) - Full system design

## Common Issues & Solutions

### Multi-Tenancy References
When seeing `request.tenant` in views, this currently fails because middleware expects tenant but models aren't properly configured. Either:
- **Temporary Fix**: Remove tenant filtering in `get_queryset()` - replace `Company.objects.filter(tenant=request.tenant)` with `Company.objects.all()`
- **Proper Fix**: Complete multi-tenancy setup per CODEBASE_ANALYSIS document Option B
- **Do NOT** just remove middleware - it's in MIDDLEWARE list but other configs are missing

### AI Service Failures
`GeminiAIService` returns mock data if `GOOGLE_API_KEY` not configured. Check logs for:
```python
# In ai_services/services.py - always returns dict even on error
except Exception as e:
    result = {'vision_statement': f"...fallback...", ...}
```
**Test if AI is working**: Look for real generation vs "Based on {industry} industry..." fallback text

### CORS Issues
Frontend must run on **localhost:3000** (NOT 127.0.0.1) to match `CORS_ALLOWED_ORIGINS` in settings.py.
- If using different port, update settings.py: `CORS_ALLOWED_ORIGINS = ['http://localhost:YOUR_PORT']`
- If seeing CORS errors, check both URL and port match exactly

### Database Connection Issues
- Neon PostgreSQL requires `sslmode=require` and `channel_binding=require` (already in settings.py)
- Credentials are HARDCODED in settings.py lines 103-109 - do NOT commit changes to this file
- Connection string format: `postgresql://user:pass@host:5432/dbname?sslmode=require`

### Frontend API Errors
```typescript
// Common issue: Token expired
// apiClient.ts auto-redirects to /auth/login on 401
// But NO automatic token refresh implemented yet

// Field name mismatch:
// Backend expects snake_case (target_audience)
// Frontend might send camelCase (targetAudience)
// Solution: Convert in serializer or frontend
```

## Testing & Quality

No test suite currently implemented. When adding tests:
- Backend: Use `pytest` + `pytest-django` (add to requirements.txt)
  - Test structure: `app_name/tests/test_models.py`, `test_views.py`, `test_serializers.py`
  - Fixtures in `conftest.py` at app and project level
  - Target: 70% coverage for Phase 3
- Frontend: Use Jest + React Testing Library (already in devDependencies)
  - Test location: `__tests__/` or `component.test.tsx` next to component
  - Target: 60% coverage for Phase 3
- AI service tests MUST mock `google.generativeai.GenerativeModel` responses
- Integration tests need proper tenant context (currently blocked by multi-tenancy issue)

## Implementation Plan & Issue Tracking

**Status**: Phase 3 implemented but non-functional - 63 issues identified requiring fixes

**Full Analysis**: See [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](../CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md)

**GitHub Issues**: All issues tracked in repository issue tracker - reference by issue number when fixing

### Current Implementation Priority

**Phase 1: Critical Fixes (BLOCKING)** - Must complete before any other work
- Issue #1: Multi-tenancy middleware enabled but broken (C-01)
- Issue #2: No user registration endpoint (C-02)
- Issue #3: JWT login email/username mismatch (C-03)
- Issue #4: No tenant creation workflow (C-04)

**Timeline**: ~15 hours | **Status**: Not started

**Phase 2: High Priority Issues** (20 issues H-01 through H-15)
- Foreign key constraints, security vulnerabilities, missing features
- **Timeline**: ~30 hours | **Status**: Pending Phase 1 completion

**Phase 3: Testing Implementation**
- Backend: pytest with 70% coverage target
- Frontend: Jest with 60% coverage target
- Integration tests for full user flows
- **Timeline**: ~43 hours | **Status**: Pending Phase 2 completion

**Phase 4: Production Readiness** (Optional - Post-MVP)
- Medium/Low priority issues (28 remaining)
- Performance optimization
- Security hardening
- Deployment automation

### Multi-Tenancy Decision

**APPROVED: Option B - Full Multi-Tenancy Implementation**

Must properly configure schema-based multi-tenancy from the start:
- Enable `django-tenants` with proper SHARED_APPS and TENANT_APPS
- Configure DATABASE_ROUTERS for schema isolation
- Create tenant on user registration with domain routing
- Test tenant isolation rigorously

**Critical**: Do NOT temporarily disable multi-tenancy. Fix the existing broken configuration instead.

### When Fixing Issues

1. **Always reference issue number** in commits: `git commit -m "Fix #1: Enable multi-tenancy properly"`
2. **Follow implementation plan** in analysis document - includes code examples
3. **Write tests** as you implement fixes (TDD approach)
4. **Update issue** with progress comments and blockers
5. **Cross-reference dependencies** between issues

### Issue Priority Rules

- 🔴 **Critical (Blocking)**: Application doesn't work - fix immediately
- 🟠 **High**: Core features broken - fix after critical
- 🟡 **Medium**: Quality/UX issues - fix after high priority
- 🟢 **Low**: Enhancements - fix in Phase 4

### Testing Requirements

Every fix must include:
- Unit tests for models/views/services
- Integration tests for API endpoints
- Frontend component tests where applicable
- Manual testing verification

See detailed testing strategy in [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](../CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#4-testing-strategy)
