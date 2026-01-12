# AI Brand Automator - Copilot Instructions

## Project Overview

**Multi-tenant SaaS platform** for AI-powered brand building with Django + Next.js:
- **Backend**: Django 4.2 + DRF at `ai-brand-automator/` (port 8000)
- **Frontend**: Next.js 16 + React 19 + TypeScript at `ai-brand-automator-frontend/` (port 3000) 
- **Database**: PostgreSQL (Neon hosted) - multi-tenancy PARTIALLY DISABLED for MVP
- **AI**: Google Gemini 1.5 Flash for brand strategy generation

**🚨 CRITICAL STATE**: Multi-tenancy configured with `django-tenants` but in transitional MVP mode. Models have nullable `tenant` FK. Always use defensive access: `tenant = getattr(request, 'tenant', None)` in views.

## Essential Architecture

### Critical Data Flow
1. User registers via `POST /api/v1/auth/register/` (email-based auth)
2. Login with `POST /api/v1/auth/login/` (email + password → JWT tokens)
3. Create `Company` via `POST /api/v1/companies/` (auto-creates `OnboardingProgress`)
4. Generate AI strategy with `POST /api/v1/companies/{id}/generate_brand_strategy/`
5. `GeminiAIService.generate_brand_strategy()` creates vision/mission/values

### Django App Structure (SHARED vs TENANT)
- **SHARED_APPS**: `tenants`, `ai_services` (available in all schemas)
- **TENANT_APPS**: `onboarding`, `files`, `automation` (isolated per tenant, but nullable tenant FK for MVP)

### URL Routing Structure
- **Auth**: `/api/v1/auth/{register,login,refresh}/` - Email-based JWT auth in [brand_automator/urls.py](ai-brand-automator/brand_automator/urls.py)
- **Onboarding**: `/api/v1/companies/` (ViewSet) - [onboarding/urls.py](ai-brand-automator/onboarding/urls.py)
- **AI Services**: `/api/v1/ai/` - [ai_services/urls.py](ai-brand-automator/ai_services/urls.py)
- **Health**: `/health/`, `/ready/`, `/alive/` - Non-auth monitoring endpoints

## Development Workflows

### Starting Services (Required Order)
```bash
# Backend - Virtual env is ONE LEVEL UP from ai-brand-automator/
cd ai-brand-automator
source ../.venv/bin/activate  # ⚠️ .venv is in workspace root
python manage.py runserver     # → http://localhost:8000

# Frontend - Separate terminal
cd ai-brand-automator-frontend  
npm run dev                    # → http://localhost:3000
```

### Testing

**Backend** (pytest + Hypothesis property-based testing):
```bash
cd ai-brand-automator
source ../.venv/bin/activate
pytest -v                      # All tests
pytest -m unit                 # Unit tests only
pytest -m property             # Property-based tests
pytest --hypothesis-show-statistics  # Hypothesis stats
```

- **Test fixtures**: [conftest.py](ai-brand-automator/conftest.py) - Public tenant auto-created, schema reset after each test
- **Property tests**: [onboarding/tests/test_properties.py](ai-brand-automator/onboarding/tests/test_properties.py) - Hypothesis generates random data to test invariants
- **Key pattern**: `@pytest.fixture` with `SERVER_NAME='localhost'` for django-tenants compatibility

**Frontend** (Jest + React Testing Library):
```bash
cd ai-brand-automator-frontend
npm test                       # Run tests
npm test -- --coverage         # With coverage (60% threshold)
```

- Test files: `__tests__/**/*.test.tsx` or `*.test.tsx` anywhere
- Path aliases: `@/` → `src/` (configured in jest.config.js and tsconfig.json)

### Database Operations
```bash
# Standard Django (multi-tenancy disabled for migrations)
python manage.py makemigrations
python manage.py migrate

# ⚠️ Multi-tenancy note: Currently using standard migrations
# If full multi-tenancy enabled, use: migrate_schemas --shared
```

### Environment Setup
```bash
# Backend (.env at ai-brand-automator/.env):
SECRET_KEY=<django-secret>
GOOGLE_API_KEY=<gemini-api-key>
DEBUG=True
DB_NAME=<neon-db>
DB_USER=<neon-user>
DB_PASSWORD=<neon-pass>
DB_HOST=<host>.neon.tech
DB_PORT=5432

# Frontend (.env.local):
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project-Specific Patterns

### Django ViewSets & Custom Actions
AI generation endpoints use `@action(detail=True, methods=['post'])`:
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
- Fallback responses if `GOOGLE_API_KEY` not configured (returns mock data)
- Response parsing extracts sections like "Vision Statement", "Mission Statement" from AI text

### Frontend API Client
- Centralized in `src/lib/api.ts` with auto token injection
- Auto-redirects to `/auth/login` on 401 responses
- Always use `apiClient.get|post|put()` instead of raw fetch
- Token refresh mechanism: uses `refresh_token` from localStorage when `access_token` expires

### Frontend Route Protection
- `useAuth()` hook in [src/hooks/useAuth.ts](ai-brand-automator-frontend/src/hooks/useAuth.ts) checks for `access_token` in localStorage
- Client-side only (no SSR token validation)
- Pattern: Call `useAuth()` at top of protected page components
```tsx
export default function ProtectedPage() {
  useAuth(); // Redirects to login if no token
  // ... component code
}
```

### Multi-Tenancy Defensive Pattern
⚠️ **CRITICAL**: Models expect tenant but middleware is partially disabled
```python
# Always use this pattern in views:
tenant = getattr(request, 'tenant', None)
if tenant:
    queryset = Model.objects.filter(tenant=tenant)
else:
    # MVP mode - no tenant filtering
    queryset = Model.objects.filter(tenant__isnull=True)
```

## Common Issues & Solutions

### Multi-Tenancy Access Errors
When seeing `'WSGIRequest' object has no attribute 'tenant'` - middleware is enabled but broken:
```python
# Fix: Replace request.tenant with defensive access
tenant = getattr(request, 'tenant', None)
# Then handle both cases appropriately
```

### AI Service Failures
`GeminiAIService` returns mock data if `GOOGLE_API_KEY` not set. Check logs for:
```python
# Always returns dict even on error - look for "Based on..." fallback text
result = {'vision_statement': "Based on technology industry..."}
```

### CORS Issues
Frontend must run on **localhost:3000** (NOT 127.0.0.1) to match `CORS_ALLOWED_ORIGINS`.

### Authentication Flow
- Registration: `POST /api/v1/auth/register/` (email/username/password)
- Login: `POST /api/v1/auth/login/` (email/password → JWT tokens)
- Frontend stores tokens in localStorage, auto-refreshes on 401

## Key File Locations

- **Settings**: [ai-brand-automator/brand_automator/settings.py](ai-brand-automator/brand_automator/settings.py#L37-L56) - Multi-tenancy toggle
- **AI Service**: [ai-brand-automator/ai_services/services.py](ai-brand-automator/ai_services/services.py) - Gemini integration
- **API Client**: [ai-brand-automator-frontend/src/lib/api.ts](ai-brand-automator-frontend/src/lib/api.ts) - Frontend HTTP client
- **Issue Tracker**: [docs/CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](docs/CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md) - 63 known issues

## Current Status & Issues

**Status**: Phase 3 implemented but with critical bugs - see [docs/CRITICAL_FIXES_SUMMARY.md](docs/CRITICAL_FIXES_SUMMARY.md)

**Major Resolved Issues**:
- ✅ Email-based login working
- ✅ Company creation with nullable tenant field  
- ✅ Defensive tenant access in views

**Known Issues**:
- Multi-tenancy partially configured but not fully functional
- No comprehensive test suite (pytest configured but minimal tests)
- Some API endpoints missing error handling

**When fixing issues**: Always reference [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](docs/CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md) for detailed implementation guidance and use defensive programming patterns for tenant access.
