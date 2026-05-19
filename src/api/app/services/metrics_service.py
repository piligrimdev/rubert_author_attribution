import dataclasses
import uuid
from typing import List, Callable

import pandas as pd

from celery import states as celery_states
from celery.result import AsyncResult

from fastapi import HTTPException

from ..core.workers import celery
from ..schemas.requests import GetMetricsRequest
from ..schemas.responses import StartComputeTaskResponse

from ..utils.auth import hash_password, check_password, create_access_token, create_refresh_token
from ..utils.text_metrics import *

from .text_service import TextService
from .mock_worker_provider import TaskData, MockTaskCache


class MetricsService:
    def __init__(
            self,
            text_service: TextService,
            on_compute_metrics: Callable,
            async_result_fn: Callable,
    ):
        self.text_service = text_service
        self.on_compute_metrics = on_compute_metrics
        self.async_result_fn = async_result_fn

    async def start_compute_metrics_task(
            self,
            form: GetMetricsRequest,
            user_id: uuid.UUID,
            session
    ) -> StartComputeTaskResponse:
        db_texts = await self.text_service.get_texts_of_author(form.author_id, user_id, session=session)

        provided_to_task_texts = [
                                     {
                                         'author': x.author,
                                         'text': x.text
                                     }
                                     for x in db_texts
        ][:50]

        task_id = await self.on_compute_metrics(provided_to_task_texts, provided_to_task_texts[0]['author'])

        return StartComputeTaskResponse(task_id=task_id)

    async def get_compute_metrics_results(
            self,
            task_id: uuid.UUID,
    ) -> tuple[str, str]:
        if not (result := self.async_result_fn(task_id)):
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        if result.status == celery_states.FAILURE:
            raise HTTPException(status_code=500, detail=f"Task {task_id} failed")

        if result.status != celery_states.SUCCESS:
            raise HTTPException(status_code=418, detail=f"Task {task_id} is in progress")

        return result.result



@celery.task(name="metrics_compute")
def metrics_compute_celery(texts, author_name):
    df = pd.DataFrame(texts)
    return compute_author_metrics(df, author_name)


async def metrics_compute(texts: str, author_name):
    task = metrics_compute_celery.delay(texts, author_name)
    return task.id


def create_mock_async_metric_compute(mock_cache: MockTaskCache) -> Callable:
    async def mock_metrics_compute(texts: dict, author_name):
        task_uuid = uuid.uuid4()

        df = pd.DataFrame(texts)

        results = compute_author_metrics(df, author_name)

        task_data = TaskData(
            id=task_uuid,
            status="SUCCESS",
            result=results
        )

        mock_cache.put(task_uuid, task_data)
        return task_uuid

    return mock_metrics_compute