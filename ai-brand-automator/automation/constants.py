"""
Constants for the automation app.
"""
from typing import List

# Test mode constants - used for development without real LinkedIn credentials
TEST_ACCESS_TOKEN = "test_access_token_not_real"
TEST_REFRESH_TOKEN = "test_refresh_token_not_real"

# LinkedIn API limits
LINKEDIN_POST_MAX_LENGTH = 3000
LINKEDIN_TITLE_MAX_LENGTH = 200

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
