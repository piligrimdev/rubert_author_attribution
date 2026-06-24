import uuid
from typing import Callable

import structlog
from celery import states as celery_states
from fastapi import HTTPException

from ..core.workers import celery
from ..schemas.requests import EmbeddingCompareRequest
from ..schemas.responses import StartComputeTaskResponse
from ..utils.embedding_umap import compute_embedding_compare_umap
from .mock_worker_provider import MockTaskCache, TaskData
from .text_service import TextService

logger = structlog.get_logger(__name__)


def _embedding_to_list(embedding) -> list[float]:
    if embedding is None:
        raise ValueError("Text embedding is missing")
    if hasattr(embedding, "tolist"):
        return embedding.tolist()
    return list(embedding)


def _serialize_text_for_task(text) -> dict:
    return {
        "text_id": str(text.id),
        "author_id": str(text.author_id),
        "author_name": str(text.author),
        "genre": str(text.genre),
        "source": "corpus",
        "text": text.text,
        "embedding": _embedding_to_list(text.embedding),
    }


class EmbeddingCompareService:
    def __init__(
        self,
        text_service: TextService,
        on_compute_embedding_compare: Callable,
        async_result_fn: Callable,
    ):
        self.text_service = text_service
        self.on_compute_embedding_compare = on_compute_embedding_compare
        self.async_result_fn = async_result_fn

    async def start_compute_embedding_compare_task(
        self,
        form: EmbeddingCompareRequest,
        user_id: uuid.UUID,
        session,
    ) -> StartComputeTaskResponse:
        texts_1 = await self.text_service.get_texts_of_author(
            form.author_id_1, user_id, session=session
        )
        texts_2 = await self.text_service.get_texts_of_author(
            form.author_id_2, user_id, session=session
        )

        if not texts_1:
            logger.error(
                "embedding_compare.no_texts",
                author_id=str(form.author_id_1),
                user_id=str(user_id),
            )
            raise HTTPException(
                status_code=400,
                detail="Author 1 missing texts",
            )

        if not texts_2:
            logger.error(
                "embedding_compare.no_texts",
                author_id=str(form.author_id_2),
                user_id=str(user_id),
            )
            raise HTTPException(
                status_code=400,
                detail="Author 2 missing texts",
            )

        if len(texts_1) < 5:
            logger.error(
                "embedding_compare.not_enough_texts",
                author_id=str(form.author_id_1),
                user_id=str(user_id),
            )
            raise HTTPException(
                status_code=400,
                detail="Author 2 has not enough texts (min - 5)",
            )

        if len(texts_2) < 5:
            logger.error(
                "embedding_compare.not_enough_texts",
                author_id=str(form.author_id_2),
                user_id=str(user_id),
            )
            raise HTTPException(
                status_code=400,
                detail="Author 2 has not enough texts (min - 5)",
            )

        payload = {
            "texts": [_serialize_text_for_task(t) for t in texts_1 + texts_2],
            "max_per_author": form.max_per_author,
        }

        task_id = await self.on_compute_embedding_compare(payload)
        logger.debug("embedding_compare.task.created", task_id=task_id)

        return StartComputeTaskResponse(task_id=task_id)

    async def get_compute_embedding_compare_results(
        self,
        task_id: uuid.UUID,
    ) -> dict:
        task_id = str(task_id)
        if not (result := self.async_result_fn(task_id)):
            logger.error("embedding_compare.task_fetching.not_found", task_id=task_id)
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        if result.status == celery_states.FAILURE:
            logger.error("embedding_compare.task_fetching.task_failed", task_id=task_id)
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Task {task_id} failed. "
                    "Возможно, у одного из авторов недостаточно текстов для UMAP — "
                    "добавьте тексты и попробуйте позже."
                ),
            )

        if result.status != celery_states.SUCCESS:
            logger.info("embedding_compare.task_fetching.task_processing", task_id=task_id)
            raise HTTPException(status_code=418, detail=f"Task {task_id} is in progress")

        logger.info("embedding_compare.task_fetching.task_finished", task_id=task_id)
        return result.result


@celery.task(name="embedding_compare_compute")
def embedding_compare_compute_celery(payload: dict):
    logger.info("embedding_compare.task.started")
    result = compute_embedding_compare_umap(
        payload["texts"],
        max_per_author=payload.get("max_per_author", 50),
    )
    logger.info("embedding_compare.task.finished")
    return result


async def embedding_compare_compute(payload: dict):
    task = embedding_compare_compute_celery.delay(payload)
    logger.info("embedding_compare.task.delayed")
    return task.id


def create_mock_async_embedding_compare_compute(mock_cache: MockTaskCache) -> Callable:
    async def mock_embedding_compare_compute(payload: dict):
        task_uuid = uuid.uuid4()
        logger.info("embedding_compare.task_mock.started")

        results = compute_embedding_compare_umap(
            payload["texts"],
            max_per_author=payload.get("max_per_author", 50),
        )

        task_data = TaskData(
            id=task_uuid,
            status="SUCCESS",
            result=results,
        )
        logger.info("embedding_compare.task_mock.finished")

        mock_cache.put(task_uuid, task_data)
        return task_uuid

    return mock_embedding_compare_compute
