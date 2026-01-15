"""
URL configuration for the automation app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SocialProfileViewSet,
    AutomationTaskViewSet,
    ContentCalendarViewSet,
    LinkedInConnectView,
    LinkedInCallbackView,
    LinkedInDisconnectView,
    LinkedInTestConnectView,
    LinkedInPostView,
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
    # Router URLs
    path("", include(router.urls)),
]
