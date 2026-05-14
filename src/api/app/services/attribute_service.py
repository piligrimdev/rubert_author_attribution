from typing import List, Optional, Callable
import uuid

from sqlalchemy.orm import Session

from ..models.abstract_model_provider import AbstractModelProvider
from ..schemas.requests import AttributionRequest
from ..schemas.responses import (
    AttributionResponse, AttributionProba, EmbeddingResponse, NearestTextsResponse,
)


class AttributeService:
    def __init__(self, model: AbstractModelProvider, text_service, prediction_strategy: Callable):
        self.model = model
        self.text_service = text_service
        self.prediction_strategy = prediction_strategy

    async def attribute(
            self,
            text: str,
            user_id: uuid,
            k: int,
            threshold: float = 0.5,
            session: Session = None,
            author_ids: Optional[List[uuid.UUID]] = None,
    ) -> List[AttributionProba]:

        if not self.model:
            raise NotImplementedError

        if self.prediction_strategy:
            if self.model.is_embedder:
                nearest = await self.predict_nearest(
                    text,
                    user_id,
                    k,
                    session,
                    author_ids
                )
                return self.prediction_strategy(nearest.items, threshold)

        authors, probs = self.model.predict(text, k_nearest=5)
        return [
            AttributionProba(author=author, proba=proba)
            for author, proba in zip(authors, probs)
        ]

    def get_embedding(
            self, form: AttributionRequest, session: Session = None
    ) -> EmbeddingResponse:
        if not self.model:
            return [AttributionProba(author="me", proba=100)]

        emb = self.model.generate_embedding(form.text)

        return EmbeddingResponse(embedding=emb)

    async def predict_nearest(
            self,
            text: str,
            user_id,
            k: int,
            session,
            author_ids: Optional[List[uuid.UUID]] = None,
    ) -> NearestTextsResponse:
        if self.text_service is None:
            return NearestTextsResponse(items=[])
        return await self.text_service.find_nearest(
            text, user_id, k, session, author_ids=author_ids
        )