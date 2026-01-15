"""
Constants for the automation app.
"""
from typing import List

# Test mode constants - used for development without real credentials
TEST_ACCESS_TOKEN = "test_access_token_not_real"
TEST_REFRESH_TOKEN = "test_refresh_token_not_real"

# Twitter test mode constants
TWITTER_TEST_ACCESS_TOKEN = "test_twitter_access_token_not_real"
TWITTER_TEST_REFRESH_TOKEN = "test_twitter_refresh_token_not_real"

# LinkedIn API limits
LINKEDIN_POST_MAX_LENGTH = 3000
LINKEDIN_TITLE_MAX_LENGTH = 200

# Twitter/X API limits
TWITTER_POST_MAX_LENGTH = 280  # Standard tweet limit
TWITTER_POST_MAX_LENGTH_PREMIUM = 25000  # X Premium subscribers
TWITTER_MEDIA_MAX_IMAGES = 4  # Max images per tweet
TWITTER_MEDIA_MAX_VIDEO_SIZE = 512 * 1024 * 1024  # 512MB for video
TWITTER_MEDIA_MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB for images
TWITTER_MEDIA_MAX_GIF_SIZE = 15 * 1024 * 1024  # 15MB for GIFs

# Twitter supported media types
TWITTER_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]
TWITTER_VIDEO_TYPES: List[str] = ["video/mp4", "video/quicktime"]

# Editable post statuses - posts with these statuses can be edited
EDITABLE_STATUSES: List[str] = ["draft", "scheduled"]

# Supported media types (LinkedIn standards)
IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif"]
VIDEO_TYPES: List[str] = ["video/mp4"]  # LinkedIn standard: MP4 only
DOCUMENT_TYPES: List[str] = [
    "application/pdf",
    "application/msword",
    # docx
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-powerpoint",
    # pptx
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
]

# Size limits (LinkedIn standards)
MAX_IMAGE_SIZE: int = 8 * 1024 * 1024  # 8MB
MAX_VIDEO_SIZE: int = 500 * 1024 * 1024  # 500MB (LinkedIn max for organic posts)
MAX_DOCUMENT_SIZE: int = 100 * 1024 * 1024  # 100MB (LinkedIn max for documents)
