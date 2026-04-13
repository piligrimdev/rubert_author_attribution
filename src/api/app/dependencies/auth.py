import uuid
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..utils.auth import decode_access_token

_bearer_scheme = HTTPBearer()


async def _get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> uuid.UUID:
    try:
        return decode_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


CurrentUserUUID = Annotated[uuid.UUID, Depends(_get_current_user_id)]
