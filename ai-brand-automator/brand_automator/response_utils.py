"""
Consistent API response formatting utilities
"""

from rest_framework.response import Response
from rest_framework import status
from typing import Any, Dict, Optional, List


class APIResponse:
    """
    Standardized API response wrapper
    Ensures consistent response format across all endpoints
    """

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK,
        meta: Optional[Dict] = None,
    ) -> Response:
        """
        Standard success response

        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            meta: Additional metadata (pagination, etc.)

        Returns:
            DRF Response object
        """
        response_data = {"success": True, "message": message, "data": data}

        if meta:
            response_data["meta"] = meta

        return Response(response_data, status=status_code)

    @staticmethod
    def error(
        message: str = "An error occurred",
        errors: Optional[Dict | List | str] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None,
    ) -> Response:
        """
        Standard error response

        Args:
            message: Error message
            errors: Detailed error information
            status_code: HTTP status code
            error_code: Application-specific error code

        Returns:
            DRF Response object
        """
        response_data = {"success": False, "message": message}

        if errors:
            response_data["errors"] = errors

        if error_code:
            response_data["error_code"] = error_code

        return Response(response_data, status=status_code)

    @staticmethod
    def paginated(
        data: List,
        count: int,
        page: int = 1,
        page_size: int = 20,
        message: str = "Success",
    ) -> Response:
        """
        Paginated response

        Args:
            data: List of items for current page
            count: Total count of items
            page: Current page number
            page_size: Items per page
            message: Success message

        Returns:
            DRF Response object
        """
        total_pages = (count + page_size - 1) // page_size

        meta = {
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            }
        }

        return APIResponse.success(data=data, message=message, meta=meta)

    @staticmethod
    def created(
        data: Any = None, message: str = "Resource created successfully"
    ) -> Response:
        """Shorthand for created response"""
        return APIResponse.success(
            data=data, message=message, status_code=status.HTTP_201_CREATED
        )

    @staticmethod
    def no_content(message: str = "Operation completed") -> Response:
        """Shorthand for no content response"""
        return APIResponse.success(
            message=message, status_code=status.HTTP_204_NO_CONTENT
        )

    @staticmethod
    def not_found(message: str = "Resource not found") -> Response:
        """Shorthand for not found response"""
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
        )

    @staticmethod
    def unauthorized(message: str = "Authentication required") -> Response:
        """Shorthand for unauthorized response"""
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
        )

    @staticmethod
    def forbidden(message: str = "Permission denied") -> Response:
        """Shorthand for forbidden response"""
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )

    @staticmethod
    def validation_error(
        errors: Dict | List | str, message: str = "Validation failed"
    ) -> Response:
        """Shorthand for validation error response"""
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
        )

    @staticmethod
    def server_error(message: str = "Internal server error") -> Response:
        """Shorthand for server error response"""
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
        )
