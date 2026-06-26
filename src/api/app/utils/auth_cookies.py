from fastapi import Response

from .auth import (
    ACCESS_COOKIE_NAME,
    ACCESS_TOKEN_EXPIRATION_MINUTES,
    AUTH_COOKIE_PATH,
    AUTH_COOKIE_SAMESITE,
    AUTH_COOKIE_SECURE,
    REFRESH_COOKIE_NAME,
    REFRESH_TOKEN_EXPIRATION_DAYS,
)


def _cookie_params(max_age: int) -> dict:
    return {
        "httponly": True,
        "secure": AUTH_COOKIE_SECURE,
        "samesite": AUTH_COOKIE_SAMESITE,
        "max_age": max_age,
        "path": AUTH_COOKIE_PATH,
    }


def _delete_cookie_params() -> dict:
    return {
        "httponly": True,
        "secure": AUTH_COOKIE_SECURE,
        "samesite": AUTH_COOKIE_SAMESITE,
        "path": AUTH_COOKIE_PATH,
    }


def set_access_cookie(response: Response, access_token: str) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        ** _cookie_params(ACCESS_TOKEN_EXPIRATION_MINUTES * 60),
    )


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        ** _cookie_params(REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60),
    )


def clear_auth_cookies(response: Response) -> None:
    delete_params = _delete_cookie_params()
    response.delete_cookie(key=ACCESS_COOKIE_NAME, **delete_params)
    response.delete_cookie(key=REFRESH_COOKIE_NAME, **delete_params)
