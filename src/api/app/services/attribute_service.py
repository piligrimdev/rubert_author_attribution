import time
import uuid
from typing import List, Optional, Callable
import structlog
from sqlalchemy.orm import Session

from ..core.metrics import record_attribution
from ..models.abstract_model_provider import AbstractModelProvider
from ..schemas.requests import AttributionRequest
from ..schemas.responses import (
    AttributionProba, EmbeddingResponse, NearestTextsResponse,
    VotesResponse,
)

logger = structlog.get_logger(__name__)


class AttributeService:
    def __init__(
            self,
            model: AbstractModelProvider,
            text_service,
            prediction_strategy: Callable,
            model_name: str = "unknown",
    ):
        self.model = model
        self.text_service = text_service
        self.prediction_strategy = prediction_strategy
        self.model_name = model_name

    async def attribute(
            self,
            text: str,
            user_id: uuid,
            k: int,
            threshold: float = 0.5,
            session: Session = None,
            author_ids: Optional[List[uuid.UUID]] = None,
    ) -> List[AttributionProba] | VotesResponse:

        if not self.model:
            logger.error("attribution.attribute.no_model_provided_error")
            raise NotImplementedError

        start = time.perf_counter()

        if self.prediction_strategy and self.model.is_embedder:
            logger.debug("attribution.attribute.searching_nearest_embeddings.started")

            nearest = await self.predict_nearest(
                text,
                user_id,
                k,
                session,
                author_ids,
            )
            logger.debug("attribution.attribute.prediction_strategy_called")

            result = self.prediction_strategy(nearest.items, threshold)

        else:
            logger.warning("attribution.attribute.no_prediction_strategy_provided")
            logger.debug("attribution.attribute.predict_method.started")

            authors, probs = self.model.predict(text, k_nearest=5)
            result = [
                AttributionProba(author=author, proba=proba)
                for author, proba in zip(authors, probs)
            ]

        record_attribution(
            result,
            model=self.model_name,
            duration_seconds=time.perf_counter() - start,
        )

        # todo get rid of this repeating code
        if isinstance(result, VotesResponse):
            outcome = "abstain" if result.predicted is None else "predicted"
            logger.info("attribution.attribute.predict_method.finished", outcome=outcome, confidence=result.confidence)

        if isinstance(result, list) and result:
            top = max(result, key=lambda x: x.proba)
            logger.info("attribution.attribute.predict_method.finished", top_proba=top)

        return result

    def get_embedding(
            self, form: AttributionRequest, session: Session = None
    ) -> EmbeddingResponse:
        if not self.model:
            logger.error("attribution.get_embedding.no_model_provided_error")
            return [AttributionProba(author="me", proba=100)]  # todo fix

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
            logger.error("attribution.searching_nearest_embeddings.no_model_text_service_provided")
            return NearestTextsResponse(items=[])
        return await self.text_service.find_nearest(
            text, user_id, k, session, author_ids=author_ids
        )
