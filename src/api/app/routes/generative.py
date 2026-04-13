from fastapi import APIRouter

from ..core import generative_service

from ..schemas.requests import  GenerateStyledRequest
from ..schemas.responses import GenerateStyledResponse

generative_router = APIRouter(prefix="/generative", tags=["generative"])

@generative_router.post("/style_text")
async def style_text(
    form: GenerateStyledRequest,
) -> GenerateStyledResponse:
    return await generative_service.style_text(form)
