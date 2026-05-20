from fastapi import APIRouter
import structlog

from ..core.dependencies import CurrentUserUUID, session_dependency
from ..core.services import attribute_service

from ..schemas.requests import AttributionRequest, SearchNearestRequest, PredictRequest
from ..schemas.responses import AttributionResponse, NearestTextsResponse, VotesResponse

attribute_router = APIRouter()
log = structlog.get_logger(__name__)

@attribute_router.post("/embedding")
async def get_embedding(
    form: AttributionRequest,
):
    return attribute_service.get_embedding(form)


@attribute_router.post("/nearest_k", response_model=NearestTextsResponse)
async def search_nearest(
    form: SearchNearestRequest,
    user_id: CurrentUserUUID,
    session: session_dependency,
):
    log.debug("attribution.nearest_k_requested", user_id=str(user_id))
    return await attribute_service.predict_nearest(
        form.text, user_id, form.k, session, author_ids=form.author_ids
    )

@attribute_router.post("/attribute", response_model=VotesResponse)
async def predict(
    form: PredictRequest,
    user_id: CurrentUserUUID,
    session: session_dependency,
):
    log.debug("attribution.list_requested", user_id=str(user_id))
    return await attribute_service.attribute(
        form.text, user_id, form.k, form.threshold, session, author_ids=form.author_ids
    )