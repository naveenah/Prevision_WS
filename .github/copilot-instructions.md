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

## Next Development Priorities

Per architecture doc phase tracking:
1. Complete onboarding UI steps (step-2, brand assets upload)
2. Implement GCS integration in `files/services.py`
3. Wire up chat interface to `/api/v1/ai/chat/` endpoint
4. Add Celery + Redis for background automation tasks
5. Re-enable multi-tenancy after single-tenant MVP validation
