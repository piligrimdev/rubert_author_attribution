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
