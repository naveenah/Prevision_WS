# Instagram Integration Report

## Overview

This document details the complete Instagram integration implemented for the AI Brand Automator platform. The implementation mirrors the Facebook integration pattern and provides comprehensive support for Instagram Business accounts via the Facebook Graph API.

## Implementation Summary

### Backend Components

#### 1. Settings Configuration (`brand_automator/settings.py`)

Added Instagram OAuth credentials:
```python
INSTAGRAM_APP_ID = os.getenv('INSTAGRAM_APP_ID', '')
INSTAGRAM_APP_SECRET = os.getenv('INSTAGRAM_APP_SECRET', '')
INSTAGRAM_REDIRECT_URI = f'{SITE_URL}/automation?platform=instagram'
INSTAGRAM_WEBHOOK_VERIFY_TOKEN = os.getenv('INSTAGRAM_WEBHOOK_VERIFY_TOKEN', 'instagram_verify_token_123')

# Threads support (future use)
INSTAGRAM_THREADS_APP_ID = os.getenv('INSTAGRAM_THREADS_APP_ID', '')
INSTAGRAM_THREADS_SECRET_KEY = os.getenv('INSTAGRAM_THREADS_SECRET_KEY', '')
INSTAGRAM_THREADS_REDIRECT_URI = f'{SITE_URL}/automation?platform=threads'
```

#### 2. Constants (`automation/constants.py`)

Added Instagram-specific constants:
- `INSTAGRAM_TEST_ACCESS_TOKEN` - For test mode development
- `INSTAGRAM_POST_MAX_LENGTH = 2200` - Caption character limit
- `INSTAGRAM_MEDIA_MAX_IMAGES = 10` - Max carousel images
- `INSTAGRAM_MEDIA_MAX_VIDEO_SIZE = 1GB` - Video size limit
- `INSTAGRAM_MEDIA_MAX_IMAGE_SIZE = 8MB` - Image size limit
- `INSTAGRAM_STORY_MAX_VIDEO_DURATION = 60` - Seconds
- `INSTAGRAM_REEL_MAX_VIDEO_DURATION = 90` - Seconds
- `INSTAGRAM_HASHTAG_MAX = 30` - Max hashtags per post
- `INSTAGRAM_IMAGE_TYPES` - Supported image MIME types
- `INSTAGRAM_VIDEO_TYPES` - Supported video MIME types

#### 3. Models (`automation/models.py`)

Extended `SocialProfile` with Instagram fields:
- `instagram_user_id` - Instagram Business Account ID
- `instagram_username` - Instagram username
- `_instagram_access_token` - Encrypted access token
- `instagram_access_token` property - Getter/setter with encryption

New models created:
- **InstagramWebhookEvent** - Stores webhook events
  - Event types: comments, mentions, story_mentions, story_replies, message_reactions, messages, live_comments
  - Fields: event_type, sender_id, media_id, comment_id, payload, processed, read, created_at

- **InstagramResumableUpload** - Tracks large video uploads
  - Media types: IMAGE, VIDEO, CAROUSEL, REELS, STORIES
  - Status: pending, uploading, processing, completed, failed
  - Progress tracking with bytes_uploaded and file_size

#### 4. Service Class (`automation/services.py`)

Created `InstagramService` class with the following methods:

**OAuth Methods:**
- `get_authorization_url()` - Generate Facebook OAuth URL with Instagram scopes
- `exchange_code_for_token(code)` - Exchange auth code for access token
- `get_long_lived_token(short_lived_token)` - Convert to 60-day token

**Account Methods:**
- `get_user_pages(access_token)` - Get Facebook Pages linked to user
- `get_instagram_account(page_id, access_token)` - Get Instagram Business account for a Page
- `get_user_profile(access_token, ig_user_id)` - Get Instagram profile info

**Content Publishing Methods:**
- `create_media_container(ig_user_id, access_token, **kwargs)` - Create media container
- `check_container_status(container_id, access_token)` - Poll container status
- `publish_media(ig_user_id, access_token, container_id)` - Publish to feed

**Carousel Methods:**
- `create_carousel_item_container(ig_user_id, access_token, image_url)` - Create carousel item
- `create_carousel_container(ig_user_id, access_token, children, caption)` - Create carousel parent

**Stories Methods:**
- `create_story_container(ig_user_id, access_token, **kwargs)` - Create story container
- `get_stories(ig_user_id, access_token)` - Get active stories

**Reels Methods:**
- `create_reel_container(ig_user_id, access_token, video_url, **kwargs)` - Create reel container

**Media Management Methods:**
- `get_user_media(ig_user_id, access_token, limit)` - Get user's media
- `get_media(media_id, access_token)` - Get specific media details
- `delete_media(media_id, access_token)` - Note: Not supported via API

**Comment Methods:**
- `get_media_comments(media_id, access_token)` - Get comments on media
- `reply_to_comment(comment_id, access_token, message)` - Reply to comment
- `delete_comment(comment_id, access_token)` - Delete a comment

**Analytics Methods:**
- `get_account_insights(ig_user_id, access_token, metrics, period)` - Get account insights
- `get_media_insights(media_id, access_token, metrics)` - Get media insights

**Webhook Methods:**
- `verify_webhook_signature(payload, signature)` - Verify webhook authenticity
- `verify_webhook_token(token, challenge)` - Verify webhook subscription

#### 5. Views (`automation/views.py`)

Created 13 Instagram view classes:

| View | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `InstagramConnectView` | GET | `/instagram/connect/` | Start OAuth flow |
| `InstagramCallbackView` | GET | `/instagram/callback/` | Handle OAuth callback |
| `InstagramDisconnectView` | POST | `/instagram/disconnect/` | Disconnect account |
| `InstagramTestConnectView` | POST | `/instagram/test-connect/` | Test mode connection |
| `InstagramAccountsView` | GET | `/instagram/accounts/` | List available accounts |
| `InstagramSelectAccountView` | POST | `/instagram/accounts/select/` | Select active account |
| `InstagramPostView` | POST | `/instagram/post/` | Create feed post |
| `InstagramCarouselPostView` | POST | `/instagram/carousel/post/` | Create carousel post |
| `InstagramStoryView` | GET/POST | `/instagram/stories/` | Get/create stories |
| `InstagramAnalyticsView` | GET | `/instagram/analytics/` | Get account insights |
| `InstagramMediaView` | GET | `/instagram/media/` | Get user media |
| `InstagramCommentsView` | GET/POST | `/instagram/comments/` | Get/reply to comments |
| `InstagramWebhookView` | GET/POST | `/instagram/webhook/` | Webhook verification & events |
| `InstagramWebhookEventsView` | GET/POST | `/instagram/webhooks/events/` | Manage webhook events |

#### 6. URLs (`automation/urls.py`)

Added 15 URL patterns:
```python
# Instagram OAuth
path('instagram/connect/', InstagramConnectView.as_view(), name='instagram-connect'),
path('instagram/callback/', InstagramCallbackView.as_view(), name='instagram-callback'),
path('instagram/disconnect/', InstagramDisconnectView.as_view(), name='instagram-disconnect'),
path('instagram/test-connect/', InstagramTestConnectView.as_view(), name='instagram-test-connect'),

# Instagram Account Management
path('instagram/accounts/', InstagramAccountsView.as_view(), name='instagram-accounts'),
path('instagram/accounts/select/', InstagramSelectAccountView.as_view(), name='instagram-select-account'),

# Instagram Content
path('instagram/post/', InstagramPostView.as_view(), name='instagram-post'),
path('instagram/carousel/post/', InstagramCarouselPostView.as_view(), name='instagram-carousel-post'),
path('instagram/stories/', InstagramStoryView.as_view(), name='instagram-stories'),
path('instagram/media/', InstagramMediaView.as_view(), name='instagram-media'),

# Instagram Analytics
path('instagram/analytics/', InstagramAnalyticsView.as_view(), name='instagram-analytics'),
path('instagram/analytics/<str:media_id>/', InstagramAnalyticsView.as_view(), name='instagram-media-analytics'),

# Instagram Comments
path('instagram/comments/', InstagramCommentsView.as_view(), name='instagram-comments'),

# Instagram Webhooks
path('instagram/webhook/', InstagramWebhookView.as_view(), name='instagram-webhook'),
path('instagram/webhooks/events/', InstagramWebhookEventsView.as_view(), name='instagram-webhook-events'),
```

### Frontend Components

#### 1. Platform Configuration

Updated `PLATFORM_CONFIG` in `automation/page.tsx`:
- Set Instagram `available: true`
- Added Instagram to `DRAFT_KEYS`

#### 2. State Variables

Added comprehensive Instagram state:
- `showInstagramComposeModal` - Modal visibility
- `igCaption` - Post caption
- `igMediaUrls`, `igMediaPreview` - Media handling
- `igCarouselMode`, `igCarouselImages` - Carousel support
- `igStories`, `loadingIgStories` - Stories management
- `igStoryQueue`, `postingIgStory` - Story upload queue
- `igDraft` - Draft save/restore
- `igAccounts`, `currentIgAccount` - Account switching
- `igAnalytics`, `loadingIgAnalytics` - Analytics data
- `igWebhookEvents` - Webhook event tracking

#### 3. Functions Added

**Draft Functions:**
- `saveIgDraft()` - Save caption/media to localStorage
- `loadIgDraft()` - Load saved draft
- `clearIgDraft()` - Clear draft
- `restoreIgDraft()` - Restore draft to form
- `openInstagramComposeModal()` - Open modal with draft restore
- `resetInstagramComposeForm()` - Reset all form fields

**API Functions:**
- `fetchInstagramAccounts()` - Get linked IG accounts
- `handleSwitchInstagramAccount(accountId)` - Switch active account
- `fetchIgAnalytics()` - Get account insights
- `fetchIgWebhookEvents()` - Get webhook events
- `handleInstagramPost()` - Create single post
- `handleInstagramCarouselPost()` - Create carousel
- `fetchInstagramStories()` - Get active stories
- `addToIgStoryQueue(files)` - Add files to story queue
- `removeFromIgStoryQueue(id)` - Remove from queue
- `handleInstagramStoryPost()` - Post all queued stories
- `resetInstagramStoryForm()` - Clear story queue

#### 4. UI Components

**Instagram Compose Modal:**
- Draft indicator with save/restore
- Compose/Preview tab toggle
- Post type toggle (Single/Carousel)
- Caption input with character counter (2200 max)
- Media upload for single posts
- Carousel image grid (2-10 images)
- Instagram-styled preview
- Post button with loading state

**Instagram Stories Modal:**
- Active stories display
- Multi-file upload queue
- Progress indicator
- Status overlays (pending/uploading/success/failed)

**Instagram Analytics Modal:**
- Account insights grid (followers, impressions, reach, etc.)
- Recent media with engagement stats
- Test mode indicator

**Platform Card Actions:**
- "Compose Post" button
- "Create Story" button  
- "View Analytics" button
- Test Connect button

### Environment Variables Required

Add to `.env`:
```bash
INSTAGRAM_APP_ID=your_app_id
INSTAGRAM_APP_SECRET=your_app_secret
INSTAGRAM_WEBHOOK_VERIFY_TOKEN=your_verify_token
INSTAGRAM_THREADS_APP_ID=threads_app_id  # Optional, for future Threads support
INSTAGRAM_THREADS_SECRET_KEY=threads_secret  # Optional
```

### Database Migration

Migration `0009_add_instagram_models.py` created and applied:
- Added Instagram fields to SocialProfile
- Created InstagramWebhookEvent model
- Created InstagramResumableUpload model

## Testing

### Test Mode Features

When using test credentials, the system automatically enables test mode:
- Simulated posts return mock responses
- Analytics show sample data
- No actual content published to Instagram

### Manual Testing Steps

1. **Test Connection:**
   - Click "Test Connect (No Real Data)" on Instagram card
   - Verify test profile created

2. **Compose Post:**
   - Click "Compose Post" 
   - Add caption and media
   - Switch to Preview tab
   - Click "Post to Instagram"
   - Verify success message

3. **Create Story:**
   - Click "Create Story"
   - Add multiple images/videos
   - Click "Share Stories"
   - Verify progress and completion

4. **View Analytics:**
   - Click "View Analytics"
   - Verify insights display
   - Check recent media engagement

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/automation/instagram/connect/` | GET | Start OAuth |
| `/api/v1/automation/instagram/callback/` | GET | OAuth callback |
| `/api/v1/automation/instagram/disconnect/` | POST | Disconnect |
| `/api/v1/automation/instagram/test-connect/` | POST | Test connection |
| `/api/v1/automation/instagram/accounts/` | GET | List accounts |
| `/api/v1/automation/instagram/accounts/select/` | POST | Select account |
| `/api/v1/automation/instagram/post/` | POST | Create post |
| `/api/v1/automation/instagram/carousel/post/` | POST | Carousel post |
| `/api/v1/automation/instagram/stories/` | GET/POST | Stories |
| `/api/v1/automation/instagram/media/` | GET | Get media |
| `/api/v1/automation/instagram/analytics/` | GET | Account insights |
| `/api/v1/automation/instagram/analytics/<id>/` | GET | Media insights |
| `/api/v1/automation/instagram/comments/` | GET/POST | Comments |
| `/api/v1/automation/instagram/webhook/` | GET/POST | Webhooks |
| `/api/v1/automation/instagram/webhooks/events/` | GET/POST | Events |

## Known Limitations

1. **Media Deletion:** Instagram API does not support deleting published content
2. **Video Processing:** Large videos require container status polling
3. **Carousel Videos:** Instagram carousels support images only (not mixed with videos)
4. **Stories Duration:** Stories expire after 24 hours automatically
5. **Rate Limits:** Subject to Instagram/Facebook API rate limits

## Future Enhancements

1. **Threads Integration:** Basic configuration added for future Meta Threads API support
2. **Reels Publishing:** Service method ready, needs frontend UI
3. **Comment Moderation:** Bulk comment management
4. **Scheduled Posts:** Integration with ContentCalendar for future scheduling
5. **Hashtag Analytics:** Track hashtag performance

## Files Modified/Created

### Backend
- `ai-brand-automator/brand_automator/settings.py`
- `ai-brand-automator/automation/constants.py`
- `ai-brand-automator/automation/models.py`
- `ai-brand-automator/automation/services.py`
- `ai-brand-automator/automation/views.py`
- `ai-brand-automator/automation/urls.py`
- `ai-brand-automator/automation/migrations/0009_add_instagram_models.py`

### Frontend
- `ai-brand-automator-frontend/src/app/automation/page.tsx`

### Documentation
- `docs/INSTAGRAM_INTEGRATION_REPORT.md` (this file)
