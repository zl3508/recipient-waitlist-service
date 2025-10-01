from __future__ import annotations
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # NOTE: keep it minimal for Sprint 1
        response: Response = await call_next(request)
        return response