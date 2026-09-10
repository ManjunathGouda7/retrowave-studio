"""Enterprise API Key Authentication & Rate Limiting Middleware."""
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Validates API key header (X-API-Key) if RETROWAVE_API_KEY environment variable is configured.
    Exempts documentation, static assets, and health check endpoints.
    """

    EXEMPT_PREFIXES = (
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/assets",
        "/samples",
        "/favicon.ico",
        "/ws",
    )

    async def dispatch(self, request: Request, call_next):
        configured_key = os.getenv("RETROWAVE_API_KEY")

        # Open Developer Mode if no key configured
        if not configured_key:
            response = await call_next(request)
            response.headers["X-RateLimit-Tier"] = "developer-unlimited"
            return response

        path = request.url.path
        if path == "/" or any(path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES):
            return await call_next(request)

        # Check header or query param
        client_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")

        if not client_key or client_key != configured_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "detail": "Invalid or missing API key. Provide a valid 'X-API-Key' header.",
                },
                headers={"WWW-Authenticate": "ApiKey"},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Tier"] = "enterprise"
        response.headers["X-RateLimit-Limit"] = "1000"
        return response
