import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        logger.info(f"Request started: {request.method} {request.url}")

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(
            f"Request completed: {request.method} {request.url} "
            f"Status: {response.status_code} Duration: {process_time:.3f}s"
        )
        return response
