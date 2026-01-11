"""
Health check endpoint for monitoring system status
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import connection
from django.conf import settings
import logging
import time

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring
    Returns system status and component health
    """

    permission_classes = [AllowAny]

    def get(self, request):
        start_time = time.time()

        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {},
        }

        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status["components"]["database"] = {"status": "healthy"}
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            health_status["status"] = "degraded"

        # Check AI service configuration
        if settings.GOOGLE_API_KEY:
            health_status["components"]["ai_service"] = {
                "status": "configured"
            }
        else:
            health_status["components"]["ai_service"] = {
                "status": "not_configured"
            }

        # Check GCS configuration
        if settings.GS_BUCKET_NAME and settings.GS_PROJECT_ID:
            health_status["components"]["file_storage"] = {
                "status": "configured"
            }
        else:
            health_status["components"]["file_storage"] = {
                "status": "not_configured"
            }

        # Response time
        health_status["response_time_ms"] = round(
            (time.time() - start_time) * 1000, 2
        )

        # Set HTTP status code
        status_code = 200 if health_status["status"] == "healthy" else 503

        return Response(health_status, status=status_code)


class ReadinessCheckView(APIView):
    """
    Readiness check for load balancers
    Returns 200 if service is ready to accept traffic
    """

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Quick database check
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return Response({"ready": True}, status=200)
        except Exception:
            return Response({"ready": False}, status=503)


class LivenessCheckView(APIView):
    """
    Liveness check for container orchestration
    Returns 200 if application is running
    """

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"alive": True}, status=200)
