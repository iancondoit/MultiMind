"""
Error handling utilities for MasterBus API.

Implements standardized error responses according to Advisory 003.
"""
import logging
import uuid
from typing import Any, Dict, List, Optional, Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class MasterBusException(Exception):
    """
    Base exception for MasterBus API.
    
    All custom exceptions should inherit from this class to ensure
    they are properly caught and formatted by the error handler.
    """
    
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the exception.
        
        Args:
            code: Error code string (e.g., 'DATA_NOT_FOUND')
            message: Human-readable error message
            status_code: HTTP status code
            details: Additional error details
        """
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.request_id = str(uuid.uuid4())
        super().__init__(self.message)


# Common exception types
class NotFoundException(MasterBusException):
    """Exception raised when a resource cannot be found."""
    
    def __init__(self, message: str, code: str = "DATA_NOT_FOUND", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ValidationException(MasterBusException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class AuthenticationException(MasterBusException):
    """Exception raised for authentication errors."""
    
    def __init__(self, message: str, code: str = "AUTH_ERROR"):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationException(MasterBusException):
    """Exception raised for authorization errors."""
    
    def __init__(self, message: str, code: str = "AUTH_FORBIDDEN"):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class ServiceUnavailableException(MasterBusException):
    """Exception raised when a dependent service is unavailable."""
    
    def __init__(self, message: str, service_name: str):
        super().__init__(
            code="SERVICE_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"service": service_name}
        )


class ErrorHandler:
    """
    Handles exception formatting and logging for API responses.
    """
    
    @staticmethod
    def format_error_response(exception: MasterBusException) -> Dict[str, Any]:
        """
        Format an exception into a standardized error response.
        
        Args:
            exception: The exception to format
            
        Returns:
            Formatted error response dictionary
        """
        return {
            "error": {
                "code": exception.code,
                "message": exception.message,
                "details": exception.details,
                "request_id": exception.request_id
            }
        }
    
    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Handle Pydantic validation errors.
        
        Args:
            request: FastAPI request
            exc: Validation exception
            
        Returns:
            JSONResponse with formatted error
        """
        details = {}
        for error in exc.errors():
            loc = ".".join(str(item) for item in error.get("loc", []))
            if loc:
                details[loc] = error.get("msg", "Invalid value")
        
        exception = ValidationException(
            message="Validation error",
            details=details
        )
        
        logger.warning(
            f"Validation error: {exception.message}",
            extra={
                "request_id": exception.request_id,
                "details": exception.details
            }
        )
        
        return JSONResponse(
            status_code=exception.status_code,
            content=ErrorHandler.format_error_response(exception)
        )
    
    @staticmethod
    async def masterbus_exception_handler(request: Request, exc: MasterBusException) -> JSONResponse:
        """
        Handle MasterBus exceptions.
        
        Args:
            request: FastAPI request
            exc: MasterBus exception
            
        Returns:
            JSONResponse with formatted error
        """
        # Log error with appropriate severity based on status code
        if exc.status_code >= 500:
            logger.error(
                f"Server error: {exc.message}",
                extra={
                    "request_id": exc.request_id,
                    "code": exc.code,
                    "details": exc.details
                },
                exc_info=True
            )
        else:
            logger.warning(
                f"Client error: {exc.message}",
                extra={
                    "request_id": exc.request_id,
                    "code": exc.code,
                    "details": exc.details
                }
            )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorHandler.format_error_response(exc)
        ) 