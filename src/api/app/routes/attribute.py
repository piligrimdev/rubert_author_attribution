from fastapi import APIRouter

from ..core import attribute_service, CurrentUserUUID, session_dependency

from ..schemas.requests import AttributionRequest, PredictNearestRequest
from ..schemas.responses import AttributionResponse, NearestTextsResponse

attribute_router = APIRouter()

@attribute_router.post("/embedding")
async def get_embedding(
    form: AttributionRequest,
):
    return attribute_service.get_embedding(form)


@attribute_router.post("/predict", response_model=NearestTextsResponse)
async def predict_nearest(
    form: PredictNearestRequest,
    user_id: CurrentUserUUID,
    session: session_dependency,
):
    return await attribute_service.predict_nearest(
        form.text, user_id, form.k, session
    )