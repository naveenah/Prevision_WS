# End-to-End Testing Guide

**AI Brand Automator - Manual Testing Checklist**

Date: January 10, 2026  
Version: MVP 1.0  
Status: Ready for Testing

---

## Prerequisites

Before testing, ensure:
- ✅ Backend running on `http://localhost:8000`
- ✅ Frontend running on `http://localhost:3000`
- ✅ Database connected (Neon PostgreSQL)
- ✅ `GOOGLE_API_KEY` configured in backend `.env`
- ✅ Browser: Chrome/Firefox with DevTools
- ✅ Clear browser cache and localStorage

---

## Test Suite 1: Authentication Flow

### 1.1 User Registration

**Steps:**
1. Navigate to `http://localhost:3000/auth/register`
2. Fill in registration form:
   - Username: `testuser1`
   - Email: `test1@example.com`
   - Password: `SecurePass123!`
3. Click "Register"

**Expected Results:**
- ✅ Success message or redirect
- ✅ JWT tokens in localStorage (`access_token`, `refresh_token`)
- ✅ Redirect to `/onboarding` or `/dashboard`
- ✅ Tenant created in database with `schema_name='tenant_<user_id>'`

**Backend Verification:**
```bash
# Check user created
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(email='test1@example.com').exists()
True

# Check tenant created
>>> from tenants.models import Tenant
>>> Tenant.objects.all().count()
1
```

---

### 1.2 User Login

**Steps:**
1. Log out if logged in
2. Navigate to `http://localhost:3000/auth/login`
3. Enter credentials:
   - Email: `test1@example.com`
   - Password: `SecurePass123!`
4. Click "Login"

**Expected Results:**
- ✅ Success message
- ✅ JWT tokens saved to localStorage
- ✅ Redirect to `/dashboard`
- ✅ No 401 errors in Network tab

**DevTools Check:**
- Open DevTools → Application → Local Storage
- Verify `access_token` and `refresh_token` exist

---

### 1.3 Token Refresh

**Steps:**
1. Login successfully
2. Open DevTools → Console
3. Run: `localStorage.getItem('access_token')`
4. Wait 61 minutes OR manually expire token:
   ```javascript
   // Force token refresh by making API call with expired token
   fetch('http://localhost:8000/api/v1/companies/', {
     headers: {
       'Authorization': 'Bearer invalid_token'
     }
   })
   ```
5. Make any API call (navigate to dashboard)

**Expected Results:**
- ✅ Token automatically refreshed
- ✅ New `access_token` in localStorage
- ✅ No redirect to login page
- ✅ API call succeeds with new token

---

### 1.4 Authentication Guards

**Steps:**
1. Clear localStorage: `localStorage.clear()`
2. Try to access:
   - `http://localhost:3000/dashboard`
   - `http://localhost:3000/chat`
   - `http://localhost:3000/onboarding/step-1`

**Expected Results:**
- ✅ Immediate redirect to `/auth/login`
- ✅ No flash of protected content
- ✅ User cannot bypass by typing URL

---

## Test Suite 2: Onboarding Flow

### 2.1 Step 1 - Company Information

**Steps:**
1. Login as `test1@example.com`
2. Navigate to `/onboarding/step-1`
3. Fill form:
   - Company Name: `Test Corp`
   - Industry: `Technology`
   - Description: `A test company for AI brand automation`
   - Target Audience: `Small business owners`
   - Core Problem: `Lack of brand strategy`
4. Click "Next Step"

**Expected Results:**
- ✅ Form submits successfully
- ✅ Redirect to `/onboarding/step-2`
- ✅ Company created in database
- ✅ `company_id` saved to localStorage
- ✅ Progress indicator shows Step 2 active

**API Verification:**
```bash
# Check in DevTools Network tab
POST /api/v1/companies/
Status: 201 Created
Response: { "id": 1, "name": "Test Corp", ... }
```

---

### 2.2 Step 2 - Brand Details

**Steps:**
1. On `/onboarding/step-2`
2. Fill form:
   - Brand Voice: `Professional`
   - Vision Statement: `To revolutionize business automation`
   - Mission Statement: `Empower entrepreneurs with AI tools`
   - Core Values: `Innovation, Integrity, Excellence`
3. Click "Next Step"

**Expected Results:**
- ✅ Form submits successfully
- ✅ Redirect to `/onboarding/step-3`
- ✅ Company updated with brand details
- ✅ Fields converted from camelCase to snake_case
- ✅ No field name mismatch errors

**Backend Check:**
```python
>>> from onboarding.models import Company
>>> company = Company.objects.get(name='Test Corp')
>>> company.brand_voice
'professional'
>>> company.vision_statement
'To revolutionize business automation'
```

---

### 2.3 Step 3 - Target Audience

**Steps:**
1. On `/onboarding/step-3`
2. Fill form:
   - Target Audience: `Entrepreneurs aged 25-45`
   - Demographics: `Urban, tech-savvy, college-educated`
   - Psychographics: `Value efficiency, innovation-focused`
   - Pain Points: `Time constraints, limited budget`
   - Desired Outcomes: `Save time, grow revenue`
3. Click "Next Step"

**Expected Results:**
- ✅ Form submits successfully
- ✅ Redirect to `/onboarding/step-4`
- ✅ Company updated with audience data
- ✅ All required fields validated

---

### 2.4 Step 4 - Upload Assets

**Steps:**
1. On `/onboarding/step-4`
2. Click "Upload files" or drag files:
   - Upload: `logo.png` (< 10MB)
   - Upload: `brand-guide.pdf`
3. Verify files appear in list
4. Click "Next Step" or "Skip"

**Expected Results:**
- ✅ Files upload successfully
- ✅ Uploaded files displayed with sizes
- ✅ Asset types detected (logo, document)
- ✅ Progress bar shows during upload
- ✅ Can skip if no files

**API Verification:**
```bash
POST /api/v1/assets/upload/
Status: 201 Created
Response: { "id": 1, "file_name": "logo.png", ... }
```

---

### 2.5 Step 5 - Review & Generate

**Steps:**
1. On `/onboarding/step-5`
2. Review all entered data:
   - Company information displayed
   - Brand details visible
   - Target audience shown
3. Click "✨ Generate Brand Strategy with AI"
4. Wait for AI generation (5-10 seconds)
5. Review AI-generated content:
   - Vision Statement
   - Mission Statement
   - Core Values (bullet list)
   - Positioning Statement
6. Click "🎨 Generate Brand Identity"
7. Click "Complete & Go to Dashboard"

**Expected Results:**
- ✅ All entered data displays correctly
- ✅ "Generate Brand Strategy" button works
- ✅ Loading state shows while generating
- ✅ AI-generated content appears in indigo cards
- ✅ Vision, mission, values, positioning all populated
- ✅ "Generate Brand Identity" button appears after strategy
- ✅ Redirect to `/dashboard` on completion

**AI Generation Check:**
```python
>>> company.refresh_from_db()
>>> company.vision_statement
'To revolutionize the way small businesses...'  # AI-generated, not manual
>>> company.mission_statement
'We empower entrepreneurs by...'
>>> company.values
['Innovation', 'Customer-Centric', 'Excellence']
```

---

## Test Suite 3: Dashboard

### 3.1 Dashboard Data Display

**Steps:**
1. Navigate to `/dashboard`
2. Observe overview cards:
   - Total Assets
   - AI Interactions
   - Companies
   - Chat Sessions

**Expected Results:**
- ✅ Real counts from API (not hardcoded)
- ✅ Assets count = number of uploaded files
- ✅ AI Interactions count > 0 (from brand strategy generation)
- ✅ Companies count = 1
- ✅ Chat Sessions count reflects actual sessions

**Loading State:**
- ✅ Skeleton loaders appear initially
- ✅ Data populates after API calls

---

### 3.2 Recent Activity Feed

**Steps:**
1. Check Recent Activity section
2. Verify activities shown:
   - AI generation events
   - Asset uploads
   - Company updates

**Expected Results:**
- ✅ Activities display in chronological order (newest first)
- ✅ Timestamps formatted correctly ("X minutes/hours/days ago")
- ✅ Activity descriptions accurate
- ✅ Shows "No recent activity" if none exists
- ✅ Maximum 5 activities displayed

---

## Test Suite 4: AI Chat Interface

### 4.1 Chat Initialization

**Steps:**
1. Navigate to `/chat`
2. Observe chat interface

**Expected Results:**
- ✅ Chat interface loads
- ✅ Message input field visible
- ✅ Send button enabled
- ✅ No errors in console

---

### 4.2 Send Chat Message

**Steps:**
1. Type message: `Help me create a social media strategy`
2. Click "Send" or press Enter
3. Wait for AI response

**Expected Results:**
- ✅ Message appears in chat
- ✅ Loading indicator while waiting
- ✅ AI response appears
- ✅ Response relevant to brand/company data
- ✅ Message saved to chat history
- ✅ Can send multiple messages in conversation

**API Verification:**
```bash
POST /api/v1/ai/chat/
Request: { "message": "Help me create..." }
Response: {
  "session_id": "...",
  "response": "Based on your brand...",
  "timestamp": "..."
}
```

---

## Test Suite 5: API Integration

### 5.1 CORS Functionality

**Steps:**
1. Open DevTools → Network tab
2. Make any API call (navigate to dashboard)
3. Check request headers

**Expected Results:**
- ✅ `Authorization: Bearer <token>` sent
- ✅ `Content-Type: application/json` sent
- ✅ No CORS errors in console
- ✅ Response headers include `Access-Control-Allow-Origin`

---

### 5.2 Error Handling

**Steps:**
1. Try invalid login:
   - Email: `wrong@example.com`
   - Password: `wrongpass`
2. Try submitting incomplete form (Step 1 without name)
3. Try accessing non-existent company: `/api/v1/companies/999/`

**Expected Results:**
- ✅ Invalid login shows error message
- ✅ Form validation prevents submission
- ✅ 404 errors display user-friendly messages
- ✅ No unhandled exceptions
- ✅ API returns proper error codes (400, 401, 404)

---

## Test Suite 6: Security

### 6.1 Authentication Required

**Steps:**
1. Clear localStorage
2. Try to access API directly:
   ```bash
   curl http://localhost:8000/api/v1/companies/
   ```

**Expected Results:**
- ✅ Returns 401 Unauthorized
- ✅ Error message: "Authentication credentials were not provided"

---

### 6.2 Tenant Isolation

**Steps:**
1. Register second user: `test2@example.com`
2. Create company for test2
3. Try to access test1's company as test2

**Expected Results:**
- ✅ test2 cannot see test1's companies
- ✅ Separate tenant schemas isolate data
- ✅ API filtering by tenant works correctly

---

## Test Suite 7: Edge Cases

### 7.1 Network Failure

**Steps:**
1. Open DevTools → Network tab
2. Throttle to "Offline"
3. Try to submit form

**Expected Results:**
- ✅ Error message displays
- ✅ No app crash
- ✅ Retry succeeds when online

---

### 7.2 Long AI Generation

**Steps:**
1. Generate brand strategy with complex company
2. Observe loading states

**Expected Results:**
- ✅ Loading spinner persists
- ✅ Button disabled during generation
- ✅ No timeout errors (< 30 seconds)

---

### 7.3 File Upload Limits

**Steps:**
1. Try to upload:
   - File > 10MB
   - Unsupported file type (.exe)
   - Many files at once (20+)

**Expected Results:**
- ✅ Large files rejected with error
- ✅ Invalid types rejected
- ✅ Multiple uploads handled gracefully

---

## Test Suite 8: Browser Compatibility

### 8.1 Chrome

**Steps:**
1. Test full flow in Chrome
2. Check DevTools console for errors

**Expected Results:**
- ✅ All features work
- ✅ No console errors
- ✅ UI renders correctly

---

### 8.2 Firefox

**Steps:**
1. Repeat full flow in Firefox

**Expected Results:**
- ✅ Same functionality as Chrome
- ✅ No browser-specific issues

---

### 8.3 Safari (if available)

**Steps:**
1. Test authentication and onboarding

**Expected Results:**
- ✅ JWT tokens work
- ✅ API calls succeed

---

## Performance Benchmarks

### API Response Times

Measure using DevTools Network tab:

| Endpoint | Target | Actual | Pass/Fail |
|----------|--------|--------|-----------|
| POST /auth/login/ | < 500ms | ___ms | ⬜ |
| POST /companies/ | < 300ms | ___ms | ⬜ |
| GET /companies/ | < 200ms | ___ms | ⬜ |
| POST /generate_brand_strategy/ | < 10s | ___ms | ⬜ |
| POST /ai/chat/ | < 5s | ___ms | ⬜ |
| POST /assets/upload/ | < 3s | ___ms | ⬜ |

---

## Known Issues / Limitations

Document any issues found during testing:

1. ⬜ Issue description
   - Steps to reproduce
   - Expected vs actual behavior
   - Severity: 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low

---

## Testing Completion Checklist

- ⬜ All Test Suite 1 tests pass (Authentication)
- ⬜ All Test Suite 2 tests pass (Onboarding)
- ⬜ All Test Suite 3 tests pass (Dashboard)
- ⬜ All Test Suite 4 tests pass (Chat)
- ⬜ All Test Suite 5 tests pass (API Integration)
- ⬜ All Test Suite 6 tests pass (Security)
- ⬜ All Test Suite 7 tests pass (Edge Cases)
- ⬜ All Test Suite 8 tests pass (Browser Compatibility)
- ⬜ Performance benchmarks meet targets
- ⬜ No critical or high-severity bugs

---

## Sign-Off

**Tester**: ________________  
**Date**: ________________  
**Result**: ⬜ PASS / ⬜ FAIL  

**Notes**:
```
(Add any additional observations or recommendations)
```

---

**Next Steps After Testing:**
1. Fix any critical/high bugs found
2. Document medium/low bugs for future sprints
3. Prepare for production deployment
4. Plan Phase 2 features

