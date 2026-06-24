import uuid
from typing import List
import structlog
from fastapi import APIRouter
from starlette.responses import Response

from ..core.dependencies import CurrentUserUUID, session_dependency
from ..core.services import  text_service, embedding_compare_service
from ..schemas.requests import CreateTextForm, EditTextForm, EmbeddingCompareRequest
from ..schemas.responses import TextItemResponse, TextEditResponse, EmbeddingUmapResponse, StartComputeTaskResponse

texts_routes = APIRouter(prefix="/texts", tags=["texts"])

log = structlog.get_logger(__name__)


@texts_routes.get("", response_model=List[TextItemResponse])
async def list_available_texts(user_id: CurrentUserUUID, session: session_dependency):
    log.debug("texts.list_text_requested", user_id=str(user_id))
    return await text_service.list_available(user_id=user_id, session=session)


@texts_routes.get("/by_author/{author_id}", response_model=List[TextItemResponse])
async def get_texts_by_author(
    author_id: uuid.UUID,
    user_id: CurrentUserUUID,
    session: session_dependency,
):
    log.debug("texts.text_by_author_requested", author_id=author_id, user_id=str(user_id))
    return await text_service.get_texts_of_author_formatted(author_id, user_id, session)


@texts_routes.post("/add", response_model=TextItemResponse)
async def add_text(
    form: CreateTextForm,
    user_id: CurrentUserUUID,
    session: session_dependency,
):
    log.debug("texts.add_text_requested", user_id=str(user_id))
    return await text_service.add_text(form, user_id, session)

@texts_routes.patch("/{text_id}", response_model=TextEditResponse)
async def edit_text(
    text_id: str,
    form: EditTextForm,
    user_id: CurrentUserUUID,
    session: session_dependency,
):
    log.debug("texts.edit_text_requested", user_id=str(user_id))
    return await text_service.edit_text(text_id, form, user_id, session)

@texts_routes.delete("/{text_id}")
async def delete_text(
        text_id: str,
        user_id: CurrentUserUUID,
        session: session_dependency
):
    log.debug("texts.delete_requested", user_id=str(user_id))
    await text_service.delete_text(text_id, user_id, session)
    return Response(status_code=204)

@texts_routes.post("/embedding_compare", response_model=StartComputeTaskResponse)
async def start_embedding_compare_task_endpoint(
    form: EmbeddingCompareRequest,
    user_id: CurrentUserUUID,
    session: session_dependency,
):
    log.debug("texts.embedding_compare_requested", user_id=str(user_id))
    return await embedding_compare_service.start_compute_embedding_compare_task(
        form, user_id, session
    )


@texts_routes.get("/embedding_compare/{task_id}", response_model=EmbeddingUmapResponse)
async def get_embedding_compare_task_results_endpoint(
    task_id: uuid.UUID,
    user_id: CurrentUserUUID,
):
    log.debug(
        "texts.embedding_compare_task_status_requested",
        user_id=str(user_id),
        task_id=str(task_id),
    )
    return await embedding_compare_service.get_compute_embedding_compare_results(task_id)