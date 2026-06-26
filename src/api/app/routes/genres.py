from http.client import HTTPResponse
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Form, UploadFile
from starlette.responses import Response

from ..core.dependencies import (
    CurrentUserUUID,
    session_dependency,
)
from ..core.services import (
    genre_service,
)
from ..schemas.responses import (
    GenreResponse,
)

genre_routes = APIRouter(prefix="/genres", tags=["genres"])
log = structlog.get_logger(__name__)


@genre_routes.get("")
async def get_genres(user_id: CurrentUserUUID, session: session_dependency):
    log.debug("genres.list_requested", user_id=str(user_id))
    return await genre_service.list_all(session=session)

