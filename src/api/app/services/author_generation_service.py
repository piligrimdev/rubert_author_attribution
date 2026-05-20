from typing import List
import structlog
from sqlalchemy.orm import Session

from ..models.abstract_generative_model_provier import AbstractGenerativeModelProvider
from ..schemas.requests import GenerateStyledRequest
from ..schemas.responses import GenerateStyledResponse

logger = structlog.get_logger(__name__)

class GenerativeService:
    def __init__(self, model: AbstractGenerativeModelProvider):
        self.model = model

    async def style_text(
            self, form: GenerateStyledRequest
    ) -> GenerateStyledResponse:
        if not self.model:
            logger.error("stylization.style_text.no_model_provided_error")
            return GenerateStyledResponse(text="No model provided")

        logger.debug("stylization.generate_text.started")
        styled_text = await self.model.generate(form.text)

        return GenerateStyledResponse(text=styled_text)
