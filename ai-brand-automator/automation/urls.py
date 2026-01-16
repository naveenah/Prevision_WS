"""
URL configuration for the automation app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SocialProfileViewSet,
    AutomationTaskViewSet,
    ContentCalendarViewSet,
    # LinkedIn views
    LinkedInConnectView,
    LinkedInCallbackView,
    LinkedInDisconnectView,
    LinkedInTestConnectView,
    LinkedInPostView,
    LinkedInMediaUploadView,
    LinkedInVideoStatusView,
    LinkedInDocumentStatusView,
    LinkedInAnalyticsView,
    # Twitter views
    TwitterConnectView,
    TwitterCallbackView,
    TwitterDisconnectView,
    TwitterTestConnectView,
    TwitterPostView,
    TwitterValidateTweetView,
    TwitterMediaUploadView,
    TwitterMediaStatusView,
    TwitterDeleteTweetView,
    TwitterAnalyticsView,
    TwitterWebhookView,
    TwitterWebhookEventsView,
)

router = DefaultRouter()
router.register(r"social-profiles", SocialProfileViewSet, basename="social-profile")
router.register(r"tasks", AutomationTaskViewSet, basename="automation-task")
router.register(
    r"content-calendar", ContentCalendarViewSet, basename="content-calendar"
)

urlpatterns = [
    # LinkedIn OAuth
    path("linkedin/connect/", LinkedInConnectView.as_view(), name="linkedin-connect"),
    path(
        "linkedin/callback/", LinkedInCallbackView.as_view(), name="linkedin-callback"
    ),
    path(
        "linkedin/disconnect/",
        LinkedInDisconnectView.as_view(),
        name="linkedin-disconnect",
    ),
    path(
        "linkedin/test-connect/",
        LinkedInTestConnectView.as_view(),
        name="linkedin-test-connect",
    ),
    path("linkedin/post/", LinkedInPostView.as_view(), name="linkedin-post"),
    path(
        "linkedin/media/upload/",
        LinkedInMediaUploadView.as_view(),
        name="linkedin-media-upload",
    ),
    path(
        "linkedin/video/status/<str:asset_urn>/",
        LinkedInVideoStatusView.as_view(),
        name="linkedin-video-status",
    ),
    path(
        "linkedin/document/status/<str:document_urn>/",
        LinkedInDocumentStatusView.as_view(),
        name="linkedin-document-status",
    ),
    # LinkedIn Analytics
    path(
        "linkedin/analytics/",
        LinkedInAnalyticsView.as_view(),
        name="linkedin-analytics",
    ),
    path(
        "linkedin/analytics/<path:post_urn>/",
        LinkedInAnalyticsView.as_view(),
        name="linkedin-analytics-post",
    ),
    # Twitter/X OAuth
    path("twitter/connect/", TwitterConnectView.as_view(), name="twitter-connect"),
    path("twitter/callback/", TwitterCallbackView.as_view(), name="twitter-callback"),
    path(
        "twitter/disconnect/",
        TwitterDisconnectView.as_view(),
        name="twitter-disconnect",
    ),
    path(
        "twitter/test-connect/",
        TwitterTestConnectView.as_view(),
        name="twitter-test-connect",
    ),
    path("twitter/post/", TwitterPostView.as_view(), name="twitter-post"),
    path(
        "twitter/validate/",
        TwitterValidateTweetView.as_view(),
        name="twitter-validate",
    ),
    path(
        "twitter/media/upload/",
        TwitterMediaUploadView.as_view(),
        name="twitter-media-upload",
    ),
    path(
        "twitter/media/status/<str:media_id>/",
        TwitterMediaStatusView.as_view(),
        name="twitter-media-status",
    ),
    path(
        "twitter/tweet/<str:tweet_id>/",
        TwitterDeleteTweetView.as_view(),
        name="twitter-delete-tweet",
    ),
    # Twitter Analytics
    path(
        "twitter/analytics/",
        TwitterAnalyticsView.as_view(),
        name="twitter-analytics",
    ),
    path(
        "twitter/analytics/<str:tweet_id>/",
        TwitterAnalyticsView.as_view(),
        name="twitter-analytics-tweet",
    ),
    # Twitter Webhooks
    path(
        "twitter/webhook/",
        TwitterWebhookView.as_view(),
        name="twitter-webhook",
    ),
    path(
        "twitter/webhooks/events/",
        TwitterWebhookEventsView.as_view(),
        name="twitter-webhook-events",
    ),
    # Router URLs
    path("", include(router.urls)),
]
