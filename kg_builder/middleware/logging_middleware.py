"""
Enhanced logging middleware for FastAPI.
Logs all incoming requests, responses, and timing information.
"""
import logging
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
import io

logger = logging.getLogger("kg_builder.middleware")


class DetailedLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs detailed information about all requests and responses.

    Features:
    - Request method, path, query params, headers
    - Request body (for POST/PUT/PATCH)
    - Response status code, headers
    - Response body
    - Processing time
    - Client information
    """

    def __init__(self, app, log_request_body: bool = True, log_response_body: bool = True):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log details."""
        start_time = time.time()

        # Generate request ID
        request_id = f"{int(start_time * 1000000)}"

        # Log request details
        await self._log_request(request, request_id)

        # Process request
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Capture response body if needed
            response_body = b""
            if self.log_response_body:
                # Read response body
                if isinstance(response, StreamingResponse):
                    # Handle streaming response
                    response_body_chunks = []
                    async for chunk in response.body_iterator:
                        response_body_chunks.append(chunk)
                    response_body = b"".join(response_body_chunks)

                    # Create new response with captured body
                    response = Response(
                        content=response_body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type
                    )
                else:
                    # For regular Response objects, body is in the response.body attribute
                    if hasattr(response, 'body'):
                        response_body = response.body

            # Log response details
            await self._log_response(
                request, response, process_time, request_id, response_body
            )

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"[REQUEST-ERROR] [{request_id}] "
                f"{request.method} {request.url.path} - "
                f"Error: {str(e)} - "
                f"Time: {process_time:.4f}s",
                exc_info=True
            )
            raise

    async def _log_request(self, request: Request, request_id: str):
        """Log detailed request information."""
        # Basic request info
        logger.info(
            f"[REQUEST-START] [{request_id}] "
            f"{request.method} {request.url.path}"
        )

        # Query parameters
        if request.query_params:
            logger.debug(
                f"[REQUEST-QUERY] [{request_id}] "
                f"Params: {dict(request.query_params)}"
            )

        # Headers (excluding sensitive ones)
        safe_headers = {
            k: v for k, v in request.headers.items()
            if k.lower() not in ['authorization', 'cookie', 'x-api-key']
        }
        logger.debug(
            f"[REQUEST-HEADERS] [{request_id}] "
            f"Headers: {json.dumps(safe_headers, indent=2)}"
        )

        # Client info
        client_host = request.client.host if request.client else "unknown"
        client_port = request.client.port if request.client else "unknown"
        logger.info(
            f"[REQUEST-CLIENT] [{request_id}] "
            f"Client: {client_host}:{client_port}"
        )

        # Request body (for POST/PUT/PATCH)
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Read body
                body = await request.body()

                # Try to parse as JSON for pretty printing
                try:
                    body_json = json.loads(body)
                    logger.info(
                        f"[REQUEST-BODY] [{request_id}] "
                        f"Body: {json.dumps(body_json, indent=2)}"
                    )
                except json.JSONDecodeError:
                    # Log as string if not JSON
                    body_str = body.decode('utf-8', errors='replace')
                    if len(body_str) > 1000:
                        body_str = body_str[:1000] + "... (truncated)"
                    logger.info(
                        f"[REQUEST-BODY] [{request_id}] "
                        f"Body: {body_str}"
                    )

                # Important: recreate the receive function to make body readable again
                async def receive():
                    return {"type": "http.request", "body": body}

                request._receive = receive

            except Exception as e:
                logger.warning(
                    f"[REQUEST-BODY-ERROR] [{request_id}] "
                    f"Could not read body: {str(e)}"
                )

    async def _log_response(
        self,
        request: Request,
        response: Response,
        process_time: float,
        request_id: str,
        response_body: bytes
    ):
        """Log detailed response information."""
        # Basic response info
        status_level = "INFO" if response.status_code < 400 else "WARNING" if response.status_code < 500 else "ERROR"
        log_func = getattr(logger, status_level.lower())

        log_func(
            f"[RESPONSE] [{request_id}] "
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )

        # Response headers
        logger.debug(
            f"[RESPONSE-HEADERS] [{request_id}] "
            f"Headers: {json.dumps(dict(response.headers), indent=2)}"
        )

        # Response body
        if self.log_response_body and response_body:
            try:
                # Try to parse as JSON for pretty printing
                body_json = json.loads(response_body)

                # Truncate large responses
                body_str = json.dumps(body_json, indent=2)
                if len(body_str) > 2000:
                    body_str = body_str[:2000] + "\n... (truncated)"

                logger.debug(
                    f"[RESPONSE-BODY] [{request_id}] "
                    f"Body: {body_str}"
                )
            except json.JSONDecodeError:
                # Log as string if not JSON
                body_str = response_body.decode('utf-8', errors='replace')
                if len(body_str) > 2000:
                    body_str = body_str[:2000] + "... (truncated)"
                logger.debug(
                    f"[RESPONSE-BODY] [{request_id}] "
                    f"Body: {body_str}"
                )
            except Exception as e:
                logger.warning(
                    f"[RESPONSE-BODY-ERROR] [{request_id}] "
                    f"Could not log body: {str(e)}"
                )


class FunctionCallLoggingDecorator:
    """Decorator to log function entry, exit, and timing."""

    def __init__(self, logger_name: str = None):
        self.logger_name = logger_name

    def __call__(self, func):
        """Wrap the function with logging."""
        import functools

        func_logger = logging.getLogger(self.logger_name or func.__module__)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            func_name = func.__qualname__
            start_time = time.time()

            # Log entry
            func_logger.info(f"[FUNC-START] {func_name} - Args: {args}, Kwargs: {kwargs}")

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # Log success
                func_logger.info(
                    f"[FUNC-END] {func_name} - "
                    f"Success - Time: {duration:.4f}s"
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Log error
                func_logger.error(
                    f"[FUNC-ERROR] {func_name} - "
                    f"Error: {str(e)} - Time: {duration:.4f}s",
                    exc_info=True
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            func_name = func.__qualname__
            start_time = time.time()

            # Log entry
            func_logger.info(f"[FUNC-START] {func_name} - Args: {args}, Kwargs: {kwargs}")

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Log success
                func_logger.info(
                    f"[FUNC-END] {func_name} - "
                    f"Success - Time: {duration:.4f}s"
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Log error
                func_logger.error(
                    f"[FUNC-ERROR] {func_name} - "
                    f"Error: {str(e)} - Time: {duration:.4f}s",
                    exc_info=True
                )
                raise

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper


# Convenience function
def log_function_calls(logger_name: str = None):
    """
    Decorator to log function calls with timing.

    Usage:
        @log_function_calls("my.logger")
        async def my_function(arg1, arg2):
            ...
    """
    return FunctionCallLoggingDecorator(logger_name)
