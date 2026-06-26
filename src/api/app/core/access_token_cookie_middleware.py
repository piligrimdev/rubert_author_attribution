from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from ..utils.auth import ACCESS_COOKIE_NAME


class AccessTokenCookieMiddleware(BaseHTTPMiddleware):
    """для получения auth токена из cookie для секюрности фронта."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if not request.headers.get("authorization"):
            access_token = request.cookies.get(ACCESS_COOKIE_NAME)
            if access_token:
                headers = MutableHeaders(scope=request.scope)
                headers["authorization"] = f"Bearer {access_token}"

        return await call_next(request)
