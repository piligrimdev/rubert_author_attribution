from typing import List

from sqlalchemy.orm import Session

from ..models.abstract_generative_model_provier import AbstractGenerativeModelProvider
from ..schemas.requests import GenerateStyledRequest
from ..schemas.responses import GenerateStyledResponse


class GenerativeService:
    def __init__(self, model: AbstractGenerativeModelProvider):
        self.model = model

    async def style_text(
            self, form: GenerateStyledRequest
    ) -> GenerateStyledResponse:
        if not self.model:
            return GenerateStyledResponse(text="No model provided")

        styled_text = await self.model.generate(form.text)

        return GenerateStyledResponse(text=styled_text)
