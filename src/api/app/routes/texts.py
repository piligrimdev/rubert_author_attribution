import uuid
from typing import List

from fastapi import APIRouter

from ..core.dependencies import CurrentUserUUID, session_dependency
from ..core.services import  text_service
from ..schemas.requests import CreateTextForm
from ..schemas.responses import TextItemResponse

texts_routes = APIRouter(prefix="/texts", tags=["texts"])


@texts_routes.get("", response_model=List[TextItemResponse])
async def list_available_texts(user_id: CurrentUserUUID, session: session_dependency):
    return await text_service.list_available(user_id=user_id, session=session)


@texts_routes.get("/by_author/{author_id}", response_model=List[TextItemResponse])
async def get_texts_by_author(
    author_id: uuid.UUID,
    user_id: CurrentUserUUID,
    session: session_dependency,
):
    return await text_service.get_texts_of_author(author_id, user_id, session)


@texts_routes.post("/add", response_model=TextItemResponse)
async def add_text(
    form: CreateTextForm,
    user_id: CurrentUserUUID,
    session: session_dependency,
):
    return await text_service.add_text(form, user_id, session)
