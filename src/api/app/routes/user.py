from fastapi import APIRouter, HTTPException, Request, Response
import structlog

from ..core.dependencies import session_dependency, CurrentUserUUID
from ..core.services import user_service
from ..schemas.requests import RegisterForm, LoginForm
from ..schemas.responses import TokenResponse, UserDataResponse
from ..utils.auth import (
    REFRESH_COOKIE_NAME,
    REFRESH_TOKEN_EXPIRATION_DAYS,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)

user_router = APIRouter(prefix="/auth", tags=["Auth"])
log = structlog.get_logger(__name__)

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
    log.debug("auth.registration_requested", username=str(form.username))
    try:
        access_token, refresh_token = await user_service.register(form, session)
    except Exception:
        log.debug("auth.registration_request_error", error_message="User with this username already exists", username=str(form.username))
        raise HTTPException(status_code=409, detail="User with this username already exists")
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)

@user_router.get("/me", response_model=UserDataResponse)
async def about_me(user_id: CurrentUserUUID, session: session_dependency):
    log.debug("auth.user_data.requested", user_id=str(user_id))
    data = await user_service.get_user_by_id(user_id, session)
    return UserDataResponse(
        username=data.username,
        user_id=user_id,
        role=data.role.role_name,
    )


@user_router.post("/login", response_model=TokenResponse)
async def login(form: LoginForm, session: session_dependency, response: Response):
    log.debug("auth.login_requested", username=str(form.username))
    try:
        access_token, refresh_token = await user_service.login(form, session)
    except ValueError:
        log.debug("auth.login_request_failed", error_message="Invalid username or password", username=str(form.username))
        raise HTTPException(status_code=401, detail="Invalid username or password")
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@user_router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, response: Response):
    log.debug("auth.refresh_access_token_requested")
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        log.debug("auth.refresh_access_token_request_failed", error_message="Refresh token missing")
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        user_id = decode_refresh_token(token)
    except ValueError:
        log.debug("auth.refresh_access_token_request_failed", error_message="Invalid or expired refresh token")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    _set_refresh_cookie(response, create_refresh_token(user_id))
    return TokenResponse(access_token=create_access_token(user_id))
