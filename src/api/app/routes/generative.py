from fastapi import APIRouter
import structlog

from ..core.services import generative_service

from ..core.dependencies import CurrentUserUUID, session_dependency
from ..schemas.requests import  GenerateStyledRequest
from ..schemas.responses import GenerateStyledResponse

generative_router = APIRouter(prefix="/generative", tags=["generative"])
log = structlog.get_logger(__name__)

@generative_router.post("/style_text")
async def style_text(
    form: GenerateStyledRequest,
    user_id: CurrentUserUUID,
) -> GenerateStyledResponse:
    log.debug("stylization.stylization_requested", user_id=str(user_id))
    return await generative_service.style_text(form)
