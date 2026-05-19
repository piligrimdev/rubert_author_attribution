import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class AttributionProba(BaseModel):
    """"""

    author: str = Field(
        description="Author name"
    )
    proba: float = Field(
         description="Probability of an author to be author of this text"
    )


class AttributionResponse(BaseModel):
    """"""

    probs: List[AttributionProba]

class EmbeddingResponse(BaseModel):
    """"""

    embedding: List[List[float]]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TextItemResponse(BaseModel):
    text_id: uuid.UUID
    text: str
    author_id: uuid.UUID
    author: str
    genre: str


class NearestTextItem(BaseModel):
    text_id: uuid.UUID
    text: str
    author_id: uuid.UUID
    author: str
    distance: float


class NearestTextsResponse(BaseModel):
    items: List[NearestTextItem]

class VotesResponse(BaseModel):
    predicted: Optional[uuid.UUID]
    confidence: float
    avg_sim: float
    votes: dict[str, int]
    items: List[NearestTextItem]

class GenerateStyledResponse(BaseModel):
    text: str

class StartComputeTaskResponse(BaseModel):
    task_id: uuid.UUID = Field(description="Id of the task")

class CorpusCsvImportResult(BaseModel):
    """Results of csv importing."""

    added: int
    skipped_empty: int
    errors: int

class StartCorpusImportTaskResponse(BaseModel):
    task_id: uuid.UUID = Field(description="Id of the task")

class CorpusImportTaskStatus(BaseModel):
    task_id: uuid.UUID = Field(description="Id of the task")
    status: str = Field(description="Celery statuses: PENDING / PROGRESS / SUCCESS / FAILURE")
    progress: Optional[float] = Field(
        default=None,
        description="% of completion",
    )
    result: Optional[CorpusCsvImportResult] = Field(
        default=None,
        description="populates on task success",
    )
    error: Optional[str] = Field(
        default=None,
        description="populates on task failure, contains error message",
    )

class GenreResponse(BaseModel):
    id: uuid.UUID
    name: str
