"""
File Storage Services for BrandForge AI
Integration with Google Cloud Storage
"""
import os
from django.conf import settings
from google.cloud import storage
from google.oauth2 import service_account


class GCSService:
    """
    Service for interacting with Google Cloud Storage
    """

    def __init__(self):
        self.bucket_name = settings.GS_BUCKET_NAME
        self.project_id = settings.GS_PROJECT_ID
        self.credentials_path = settings.GS_CREDENTIALS_PATH

        # Initialize GCS client
        try:
            if self.credentials_path and os.path.exists(self.credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.client = storage.Client(
                    credentials=credentials, project=self.project_id
                )
            else:
                # Try to use default credentials (for GCP environments)
                self.client = storage.Client(project=self.project_id)
        except Exception as e:
            # Fallback: create a mock client for development
            print(f"GCS initialization failed: {e}. Using mock service.")
            self.client = None

        if self.client:
            self.bucket = self.client.bucket(self.bucket_name)
        else:
            self.bucket = None

    def upload_file(self, file_obj, file_path, content_type=None):
        """
        Upload a file to Google Cloud Storage

        Args:
            file_obj: File object to upload
            file_path: Path in GCS where to store the file
            content_type: MIME type of the file

        Returns:
            str: Public URL of the uploaded file
        """
        if not self.bucket:
            # Mock upload for development
            return f"https://storage.googleapis.com/{self.bucket_name}/{file_path}"

        try:
            blob = self.bucket.blob(file_path)

            # Set content type if provided
            if content_type:
                blob.content_type = content_type

            # Upload the file
            blob.upload_from_file(file_obj, content_type=content_type)

            # Make the file publicly accessible
            blob.make_public()

            return blob.public_url

        except Exception as e:
            raise Exception(f"Failed to upload file to GCS: {str(e)}")

    def delete_file(self, file_path):
        """
        Delete a file from Google Cloud Storage

        Args:
            file_path: Path of the file to delete
        """
        try:
            blob = self.bucket.blob(file_path)
            blob.delete()
        except Exception as e:
            raise Exception(f"Failed to delete file from GCS: {str(e)}")

    def file_exists(self, file_path):
        """
        Check if a file exists in Google Cloud Storage

        Args:
            file_path: Path of the file to check

        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            blob = self.bucket.blob(file_path)
            return blob.exists()
        except Exception:
            return False


# Global service instance
gcs_service = GCSService()
