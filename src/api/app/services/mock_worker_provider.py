import dataclasses
import uuid
from typing import Callable


@dataclasses.dataclass
class TaskData:
    id: uuid.UUID
    status: str
    result: Callable

class MockTaskCache:
    def __init__(self) -> None:
        self.tasks = {}

    def get(self, task_id: str) -> TaskData:
        key = str(task_id)
        return self.tasks.get(key)

    def put(self, task_id: str, data: TaskData):
        key = str(task_id)
        self.tasks[key] = data

def create_mock_async_result(mock_cache: MockTaskCache) -> Callable:
    def async_result(task_id: str) -> TaskData:
        return mock_cache.get(task_id)
    return async_result



