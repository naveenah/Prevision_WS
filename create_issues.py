#!/usr/bin/env python3
"""
Create GitHub issues for AI Brand Automator codebase fixes
"""

import subprocess
import time

ISSUES = [
    # CRITICAL ISSUES
    {
        "title": "🔴 C-01: Multi-tenancy middleware enabled but broken",
        "body": """**Priority**: BLOCKING | **Time**: 8-12 hours | **Dependencies**: None

## Problem
`TenantMainMiddleware` is in MIDDLEWARE list but tenant system is disabled. Every request tries to resolve `request.tenant` and fails with AttributeError.

## Fix
Enable full multi-tenancy (Option B approved):
1. Configure SHARED_APPS and TENANT_APPS
2. Set DATABASE_ROUTERS  
3. Configure TENANT_MODEL and TENANT_DOMAIN_MODEL
4. Test tenant resolution

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#c-01)"""
    },
    {
        "title": "🔴 C-02: No user registration endpoint",
        "body": """**Priority**: BLOCKING | **Time**: 4-6 hours | **Depends on**: #1

## Problem
Missing `POST /api/v1/auth/register/` endpoint. Users cannot create accounts.

## Fix
1. Create UserRegistrationSerializer
2. Create UserRegistrationView
3. Create tenant schema on registration
4. Return JWT tokens

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#c-02)"""
    },
    {
        "title": "🔴 C-03: JWT login email/username mismatch",
        "body": """**Priority**: BLOCKING | **Time**: 2-3 hours | **Dependencies**: None

## Problem
JWT expects `username`, frontend sends `email`. All logins fail with 400.

## Fix
Create custom `EmailTokenObtainPairSerializer` that accepts email instead of username.

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#c-03)"""
    },
    {
        "title": "🔴 C-04: No tenant creation workflow",  
        "body": """**Priority**: BLOCKING | **Time**: 3-4 hours | **Depends on**: #1, #2

## Problem
Company creation fails due to missing tenant foreign key.

## Fix
1. Create tenant during user registration
2. Update CompanyViewSet to use `request.tenant`
3. Auto-create OnboardingProgress with tenant

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#c-04)"""
    },
    # HIGH PRIORITY
    {
        "title": "🟠 H-01: Foreign key constraint violations on tenant fields",
        "body": """**Priority**: HIGH | **Time**: 2-3 hours | **Depends on**: #1

Ensure all tenant foreign keys work correctly after multi-tenancy is enabled. Add tests for tenant isolation.

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-01)"""
    },
    {
        "title": "🟠 H-02: Database credentials exposed in source code",
        "body": """**Priority**: HIGH | **Time**: 1 hour | **Dependencies**: None

⚠️ **SECURITY ISSUE**: Password `npg_ihO4oHanJW8e` is hardcoded in settings.py

## Immediate Actions
1. Rotate database password in Neon
2. Move credentials to .env
3. Create .env.example
4. Never commit .env

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-02)"""
    },
    {
        "title": "🟠 H-03: SECRET_KEY exposed with insecure default",
        "body": """**Priority**: HIGH | **Time**: 15 min | **Dependencies**: None

Generate new SECRET_KEY and move to environment variable.

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-03)"""
    },
    {
        "title": "🟠 H-04: File upload endpoint has hardcoded company ID",
        "body": """**Priority**: HIGH | **Time**: 2-3 hours | **Depends on**: #1

Line 124 in onboarding/views.py: `company = get_object_or_404(Company, pk=1)`

Fix to use proper company from URL and filter by tenant.

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-04)"""
    },
    {
        "title": "🟠 H-05: AI service tenant logging fails",
        "body": """**Priority**: HIGH | **Time**: 1-2 hours | **Depends on**: #1

AIGeneration.objects.create() fails because tenant parameter is not properly validated.

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-05)"""
    },
    {
        "title": "🟠 H-06: Missing GCS configuration",
        "body": """**Priority**: HIGH | **Time**: 3-4 hours | **Dependencies**: None

All GCS settings default to empty strings. File uploads return mock URLs.

1. Create GCS bucket
2. Create service account
3. Configure environment variables

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-06)"""
    },
    {
        "title": "🟠 H-07: Missing authentication decorators on API views",
        "body": """**Priority**: HIGH | **Time**: 30 min | **Dependencies**: None

⚠️ **SECURITY**: ai_services/views.py endpoints don't require authentication.

Add `@permission_classes([IsAuthenticated])` to all API views.

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-07)"""
    },
    {
        "title": "🟠 H-08: OnboardingProgress auto-creation fails",
        "body": """**Priority**: HIGH | **Time**: 1 hour | **Depends on**: #1, #4

Company save fails because tenant doesn't exist. Fix perform_create to pass tenant from request.

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-08)"""
    },
    {
        "title": "🟠 H-09: Chat session creation fails",
        "body": """**Priority**: HIGH | **Time**: 1 hour | **Depends on**: #1

ChatSession.objects.create() fails due to missing request.tenant.

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-09)"""
    },
    {
        "title": "🟠 H-10: Missing error handling in AI service",
        "body": """**Priority**: HIGH | **Time**: 3-4 hours | **Dependencies**: None

Add proper error handling, logging, and retry logic to GeminiAIService.

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-10)"""
    },
    {
        "title": "🟠 H-11: Missing component exports (TypeScript errors)",
        "body": """**Priority**: HIGH | **Time**: 15 min | **Dependencies**: None

MessageBubble.tsx and FileSearch.tsx missing `export` keywords on interfaces. Frontend doesn't compile.

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-11)"""
    },
    {
        "title": "🟠 H-12: Field name mismatches (camelCase vs snake_case)",
        "body": """**Priority**: HIGH | **Time**: 2-3 hours | **Dependencies**: None

Frontend sends camelCase, backend expects snake_case. Data is lost on save.

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-12)"""
    },
    {
        "title": "🟠 H-13: API client missing comprehensive error handling",
        "body": """**Priority**: HIGH | **Time**: 2-3 hours | **Dependencies**: None

lib/api.ts only handles 401. Add 400, 403, 500 handling and retry logic.

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-13)"""
    },
    {
        "title": "🟠 H-14: Missing authentication guards on protected pages",
        "body": """**Priority**: HIGH | **Time**: 1-2 hours | **Dependencies**: None

⚠️ **SECURITY**: No auth check on dashboard, chat, onboarding pages. Create useAuth hook.

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-14)"""
    },
    {
        "title": "🟠 H-15: Hardcoded company ID fallback in BrandForm",
        "body": """**Priority**: HIGH | **Time**: 30 min | **Dependencies**: None

Line 29: `const companyId = localStorage.getItem('company_id') || '1'` - dangerous fallback!

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#h-15)"""
    },
    # MEDIUM PRIORITY (sampling - create more later)
    {
        "title": "🟡 M-01: Missing token refresh logic",
        "body": """**Priority**: MEDIUM | **Time**: 2 hours

Users logged out after 60 minutes. Implement automatic token refresh.

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md)"""
    },
    {
        "title": "🟡 M-02: Missing onboarding steps 3-5",
        "body": """**Priority**: MEDIUM | **Time**: 8 hours

Only step-1 and step-2 exist. Need step-3 (brand strategy), step-4 (identity), step-5 (review).

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md)"""
    },
    {
        "title": "🟡 M-03: Dashboard data is static",
        "body": """**Priority**: MEDIUM | **Time**: 4 hours

Dashboard shows hardcoded data. Integrate with real API endpoints.

See: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md)"""
    },
    # META TRACKING
    {
        "title": "📋 [META] Phase 1: Critical Fixes Tracking",
        "body": """Track completion of all 4 critical blocking issues.

**Checklist**:
- [ ] #1 - Multi-tenancy enabled
- [ ] #2 - User registration
- [ ] #3 - JWT login fixed  
- [ ] #4 - Tenant creation workflow

**Goal**: Application becomes functional  
**Timeline**: Week 1 (~15 hours)  
**Status**: Not started

See full plan: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#52-phase-1-critical-fixes-week-1)"""
    },
    {
        "title": "📋 [META] Phase 2: High Priority Fixes Tracking",
        "body": """Track completion of all 20 high priority issues.

**Goal**: Core features working  
**Timeline**: Week 2-3 (~30 hours)  
**Status**: Blocked by Phase 1

See full plan: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#53-phase-2-core-features-week-2-3)"""
    },
    {
        "title": "📋 [META] Phase 3: Testing Implementation Tracking",
        "body": """Track test suite implementation.

**Checklist**:
- [ ] Backend test setup (pytest, fixtures, coverage)
- [ ] Backend unit tests (70% coverage target)
- [ ] Backend integration tests
- [ ] Frontend test setup (Jest, Testing Library)
- [ ] Frontend component tests (60% coverage)
- [ ] E2E tests (optional)

**Timeline**: Week 4 (~43 hours)  
**Status**: Blocked by Phase 2

See full plan: [CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md](CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md#54-phase-3-testing--quality-week-4)"""
    }
]

def create_issue(title, body):
    """Create a single GitHub issue"""
    try:
        result = subprocess.run(
            ['gh', 'issue', 'create', '--title', title, '--body', body],
            capture_output=True,
            text=True,
            check=True
        )
        issue_url = result.stdout.strip()
        issue_num = issue_url.split('/')[-1] if issue_url else '?'
        print(f"✅ Created #{issue_num}: {title}")
        return issue_num
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create: {title}")
        print(f"   Error: {e.stderr}")
        return None

def main():
    print("🚀 Creating GitHub issues for AI Brand Automator...\n")
    
    created = []
    failed = []
    
    for i, issue in enumerate(ISSUES, 1):
        print(f"[{i}/{len(ISSUES)}] Creating: {issue['title'][:60]}...")
        issue_num = create_issue(issue['title'], issue['body'])
        
        if issue_num:
            created.append(issue_num)
        else:
            failed.append(issue['title'])
        
        # Rate limit: 1 second between requests
        if i < len(ISSUES):
            time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully created {len(created)} issues")
    if failed:
        print(f"❌ Failed to create {len(failed)} issues:")
        for title in failed:
            print(f"   - {title}")
    print(f"{'='*60}\n")
    
    print("View all issues: gh issue list")
    print("See full details: CODEBASE_ANALYSIS_AND_IMPLEMENTATION_PLAN.md")

if __name__ == '__main__':
    main()
