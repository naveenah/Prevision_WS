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

**Status**: Phase 3 complete, Phase 4 in progress

**Completed Phases**:
- ✅ Phase 1: Foundation (Django multi-tenancy, PostgreSQL, auth)
- ✅ Phase 2: Core Backend (Onboarding APIs, GCS integration, AI services)
- ✅ Phase 3: Frontend Development (Next.js, auth UI, onboarding flow, chat)

**Major Resolved Issues**:
- ✅ Email-based login working
- ✅ Company creation with nullable tenant field  
- ✅ Defensive tenant access in views
- ✅ Comprehensive test suite (pytest + Hypothesis property tests)

---

## Phase 4: Integrations - Implementation Plan

### 4.1 Stripe Payment Integration (Priority: HIGH)

**Backend Tasks:**
1. **Create `subscriptions` Django app**
   - Models: `Subscription`, `SubscriptionPlan`, `PaymentHistory`
   - Add `stripe_customer_id` to Tenant model
   
2. **API Endpoints:**
   - `GET /api/v1/subscriptions/plans` - List available plans
   - `POST /api/v1/subscriptions/create-checkout-session` - Create Stripe checkout
   - `GET /api/v1/subscriptions/status` - Current subscription status
   - `POST /api/v1/subscriptions/webhook` - Handle Stripe webhooks
   - `POST /api/v1/subscriptions/create-portal-session` - Customer billing portal

3. **Subscription Tiers:**
   | Plan | Price | Features |
   |------|-------|----------|
   | Basic | $29/mo | Core features, 1 brand |
   | Pro | $79/mo | Advanced AI, 5 brands, automation |
   | Enterprise | $199/mo | Unlimited, team features |

**Frontend Tasks:**
1. Create `/subscription` page with plan cards
2. Create `/billing` page for subscription management
3. Add subscription status to dashboard
4. Implement checkout redirect flow

**Environment Variables Required:**
```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_BASIC=price_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_ENTERPRISE=price_...
```

### 4.2 Automation Models (Priority: MEDIUM)

**Backend Tasks:**
1. **Populate `automation` app with models:**
   - `SocialProfile` - Connected social accounts
   - `AutomationTask` - Scheduled automation jobs
   - `ContentCalendar` - Scheduled posts

2. **API Endpoints:**
   - `GET /api/v1/automation/social-profiles` - List connected profiles
   - `POST /api/v1/automation/connect/{platform}` - OAuth connect (stub)
   - `DELETE /api/v1/automation/disconnect/{platform}` - Disconnect

3. **Supported Platforms (MVP):**
   - LinkedIn (Company Pages API)
   - Twitter/X (OAuth 2.0)
   - Instagram Business (via Facebook Graph API)

**Frontend Tasks:**
1. Create `/automation` page
2. Add social connection buttons
3. Show connected accounts status

### 4.3 Webhook Handling (Priority: HIGH)

**Stripe webhook events to handle:**
- `checkout.session.completed` - New subscription
- `invoice.payment_succeeded` - Recurring payment
- `invoice.payment_failed` - Payment failure
- `customer.subscription.updated` - Plan change
- `customer.subscription.deleted` - Cancellation

### 4.4 Files to Create/Modify

**New Files:**
```
ai-brand-automator/
├── subscriptions/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py          # Subscription, Plan, PaymentHistory
│   ├── serializers.py
│   ├── views.py           # Checkout, webhook, portal
│   ├── urls.py
│   └── services.py        # Stripe service wrapper
├── automation/
│   ├── models.py          # SocialProfile, AutomationTask, ContentCalendar
│   ├── serializers.py
│   ├── views.py
│   └── urls.py

ai-brand-automator-frontend/src/
├── app/
│   ├── subscription/
│   │   └── page.tsx       # Pricing/plans page
│   ├── billing/
│   │   └── page.tsx       # Billing management
│   └── automation/
│       └── page.tsx       # Social connections
├── components/
│   ├── subscription/
│   │   ├── PlanCard.tsx
│   │   └── CheckoutButton.tsx
│   └── automation/
│       └── SocialConnectButton.tsx
```

**Modified Files:**
- `tenants/models.py` - Add `stripe_customer_id` field
- `brand_automator/urls.py` - Add subscription/automation routes
- `brand_automator/settings.py` - Add Stripe config

### Implementation Order

| Step | Task | Est. Time | Priority |
|------|------|-----------|----------|
| 4.1.1 | Create `subscriptions` app with models | 2 hours | HIGH |
| 4.1.2 | Implement Stripe checkout endpoints | 3 hours | HIGH |
| 4.1.3 | Implement webhook handler | 2 hours | HIGH |
| 4.1.4 | Frontend subscription pages | 3 hours | HIGH |
| 4.2.1 | Create automation models | 2 hours | MEDIUM |
| 4.2.2 | OAuth connection endpoints (stub) | 2 hours | MEDIUM |
| 4.2.3 | Frontend automation page | 2 hours | MEDIUM |

---

**When fixing issues**: Always reference [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](docs/CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md) for detailed implementation guidance and use defensive programming patterns for tenant access.
