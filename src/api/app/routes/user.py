from fastapi import APIRouter, HTTPException, Request, Response

from ..core.dependencies import session_dependency
from ..core.services import user_service
from ..schemas.requests import RegisterForm, LoginForm
from ..schemas.responses import TokenResponse
from ..utils.auth import (
    REFRESH_COOKIE_NAME,
    REFRESH_TOKEN_EXPIRATION_DAYS,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)

user_router = APIRouter(prefix="/auth", tags=["Auth"])


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60,
        path="/auth",
    )


@user_router.post("/register", response_model=TokenResponse)
async def register(form: RegisterForm, session: session_dependency, response: Response):
    try:
        access_token, refresh_token = await user_service.register(form, session)
    except Exception:
        raise HTTPException(status_code=409, detail="User with this username already exists")
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@user_router.post("/login", response_model=TokenResponse)
async def login(form: LoginForm, session: session_dependency, response: Response):
    try:
        access_token, refresh_token = await user_service.login(form, session)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@user_router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, response: Response):
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        user_id = decode_refresh_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    _set_refresh_cookie(response, create_refresh_token(user_id))
    return TokenResponse(access_token=create_access_token(user_id))
