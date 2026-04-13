import dataclasses
import uuid
from typing import List, Callable

import pandas as pd
from fastapi import HTTPException


from ..schemas.requests import GetMetricsRequest, StartComputeTaskResponse, GetMetricsTaskResultRequest

from ..utils.auth import hash_password, check_password, create_access_token, create_refresh_token
from ..utils.text_metrics import *

from .text_service import TextService


class MetricsService:
    def __init__(
            self,
            text_service: TextService,
            on_compute_metrics: Callable,
            task_cache
    ):
        self.text_service = text_service
        self.on_compute_metrics = on_compute_metrics
        self.task_cache = task_cache

    async def start_compute_metrics_task(
            self,
            form: GetMetricsRequest,
            user_id: uuid.UUID,
            session
    ) -> tuple[str, str]:
        db_texts = await self.text_service.get_texts_of_author(form.author_id, user_id, session=session)

        provided_to_task_texts = [
                                     {
                                         'author': x.author,
                                         'text': x.text
                                     }
                                     for x in db_texts
        ][:50]

        df = pd.DataFrame(provided_to_task_texts)
        task_id = await self.on_compute_metrics(df, provided_to_task_texts[0]['author'], self.task_cache)

        return self.task_cache.get(task_id).result

        #return StartComputeTaskResponse(task_id=task_id)

    async def get_compute_metrics_results(
            self,
            form: GetMetricsTaskResultRequest
    ) -> tuple[str, str]:
        if not (result := self.task_cache.get(form.task_id)):
            raise HTTPException(status_code=400, detail=f"Task {form.task_id} not found")

        if not result.status:
            raise HTTPException(status_code=400, detail=f"Task {form.task_id} is in progress")

        return result.data

@dataclasses.dataclass
class TaskData:
    id: uuid.UUID
    status: str
    result: dict

class MockTaskCache:
    def __init__(self) -> None:
        self.tasks = {}

    def get(self, task_id: str) -> TaskData:
        return self.tasks[task_id]

    def put(self, task_id: str, data: TaskData):
        self.tasks[task_id] = data

async def mock_metrics_compute(texts: str, author_name, tasks_cache):
    task_uuid = uuid.uuid4()

    results = compute_author_metrics(texts, author_name)

    task_data = TaskData(
        id=task_uuid,
        status="success",
        result=results
    )

    tasks_cache.put(task_uuid, task_data)
    return task_uuid


