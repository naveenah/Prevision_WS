# AI Brand Automator - Copilot Instructions

## Project Architecture

This is a **multi-tenant SaaS platform** for AI-powered brand building with:
- **Backend**: Django 4.2 + DRF at `ai-brand-automator/` (port 8000)
- **Frontend**: Next.js 16 + React 19 + TypeScript at `ai-brand-automator-frontend/` (port 3000)
- **Database**: PostgreSQL (Neon hosted) with planned schema-based multi-tenancy via `django-tenants`
- **AI**: Google Gemini 1.5 Flash via `google-generativeai` for brand strategy generation

**Critical**: Multi-tenancy infrastructure (django-tenants) is **currently disabled** in settings.py. The codebase has tenant references but runs in single-tenant mode. When referencing `request.tenant`, know this won't work until multi-tenancy is re-enabled.

## Key Components & Data Flow

### Django Apps Structure
- `onboarding/`: Company creation → Brand strategy generation → Asset uploads
- `ai_services/`: Chat sessions + AI content generation (brand strategy, identity, messaging)
- `tenants/`: Multi-tenant models (disabled but present in migrations)
- `files/`: GCS upload service (referenced but not fully implemented)
- `automation/`: Placeholder for future Celery background tasks

### Brand Creation Workflow
1. User creates `Company` via `POST /api/v1/companies/`
2. `OnboardingProgress` auto-created with `current_step='company_info'`
3. Frontend calls `POST /api/v1/companies/{id}/generate_brand_strategy/`
4. `GeminiAIService.generate_brand_strategy()` generates vision/mission/values/positioning
5. AI responses saved to Company model + `AIGeneration` logging model

### API Authentication
- JWT via `djangorestframework-simplejwt` with Bearer tokens
- Frontend stores tokens in localStorage (`access_token`, `refresh_token`)
- All API endpoints under `/api/v1/` require authentication except `/auth/login|refresh/`
- CORS configured for `localhost:3000` in development

## Development Workflows

### Running Services
```bash
# Backend (Django)
cd ai-brand-automator
source ../.venv/bin/activate  # Virtual env is in workspace root
python manage.py runserver

# Frontend (Next.js)
cd ai-brand-automator-frontend
npm run dev
```

### Database Operations
```bash
# Migrations (multi-tenancy disabled, so standard Django)
python manage.py makemigrations
python manage.py migrate

# Access Neon PostgreSQL (credentials in settings.py)
# Connection string in settings.py - avoid committing credentials
```

### Environment Configuration
- Uses `python-decouple` for settings via `.env` files (not committed)
- Key variables: `SECRET_KEY`, `DEBUG`, `GOOGLE_API_KEY`, `GS_BUCKET_NAME`
- Frontend API URL: `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`)

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
When seeing `request.tenant` in views, this currently fails. Either:
- Remove tenant filtering in `get_queryset()` temporarily
- Add try/except with fallback to `.all()`
- Wait for multi-tenancy re-enablement per settings.py comments

### AI Service Failures
`GeminiAIService` returns mock data if API key missing. Check console logs for:
```python
# In services.py - always returns dict even on error
except Exception as e:
    result = {'vision_statement': f"...fallback...", ...}
```

### CORS Issues
Frontend must run on `localhost:3000` (not 127.0.0.1) to match CORS_ALLOWED_ORIGINS. Update settings.py if different ports needed.

### Database Credentials
Neon PostgreSQL credentials are hardcoded in settings.py (should move to .env). Connection requires `sslmode=require`.

## Testing & Quality

No test suite currently implemented. When adding tests:
- Use `pytest` + `pytest-django` (add to requirements.txt)
- Test AI service with mocked Gemini responses
- Integration tests need separate test database schema

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
