from typing import List

from fastapi import APIRouter, Path
from ..schemas.requests import GetAuthorForm, CreateAuthorForm, GetMetricsRequest
from ..core import CurrentUserUUID, session_dependency, author_service, metrics_service

authors_routes = APIRouter(prefix="/authors", tags=["authors"])


@authors_routes.get("")
async def get_authors(user_id: CurrentUserUUID, session: session_dependency):
    return await author_service.list_available(user_id=user_id, session=session)

@authors_routes.get("/generative_enabled")
async def get_generative_enabled_authors(
    user_id: CurrentUserUUID, session: session_dependency
):
    return await author_service.list_generative_enabled(
        user_id=user_id, session=session
    )

@authors_routes.post("/create")
async def create_author(
    form: CreateAuthorForm, user_id: CurrentUserUUID, session: session_dependency
) -> None:
    return await author_service.create(form, user_id, session)

@authors_routes.post("/compute_metrics")
async def create_author(
    form: GetMetricsRequest, user_id: CurrentUserUUID, session: session_dependency
) -> None:
    return await metrics_service.start_compute_metrics_task(form, user_id, session)
