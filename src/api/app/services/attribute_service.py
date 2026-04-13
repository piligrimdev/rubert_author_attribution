from typing import List

from sqlalchemy.orm import Session

from ..models.abstract_model_provider import AbstractModelProvider
from ..schemas.requests import AttributionRequest
from ..schemas.responses import (
    AttributionResponse, AttributionProba, EmbeddingResponse, NearestTextsResponse,
)


class AttributeService:
    def __init__(self, model: AbstractModelProvider, text_service):
        self.model = model
        self.text_service = text_service

    def attribute(
        self, form: AttributionRequest, easy_mode: bool = False, session: Session = None
    ) -> List[AttributionProba]:
        if not self.model:
            return [AttributionProba(author="me", proba=100)]

        authors, probs = self.model.predict(form.text, k_nearest=5)
        return [
            AttributionProba(author=author, proba=proba)
            for author, proba in zip(authors, probs)
        ]

    def get_embedding(
            self, form: AttributionRequest, easy_mode: bool = False, session: Session = None
    ) -> EmbeddingResponse:
        if not self.model:
            return [AttributionProba(author="me", proba=100)]

        emb = self.model.generate_embedding(form.text)

        return EmbeddingResponse(embedding=emb)

    async def predict_nearest(
            self, text: str, user_id, k: int, session
    ) -> NearestTextsResponse:
        if self.text_service is None:
            return NearestTextsResponse(items=[])
        return await self.text_service.find_nearest(text, user_id, k, session)