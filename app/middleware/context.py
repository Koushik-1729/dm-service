from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.common.request_context import client_phone_ctx, client_id_ctx


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_phone = request.headers.get("x-client-phone")
        client_id = request.headers.get("x-client-id")

        request.state.client_phone = client_phone
        request.state.client_id = client_id

        client_phone_ctx.set(client_phone)
        client_id_ctx.set(client_id)

        response = await call_next(request)
        return response
