import uuid
from typing import List, Optional

from pydantic import BaseModel, Field


class AttributionRequest(BaseModel):
    """"""

    text: str = Field(description="Attribution text")

class GenerateStyledRequest(BaseModel):
    """"""
    author_id: uuid.UUID = Field(description="UUID of the author")
    text: str = Field(description="Text to stylize")


class GetAuthorForm(BaseModel):
    """Used in author retrieving """

    name: Optional[str] = Field(description="Author name")
    surname: Optional[str] = Field(description="Author surname")
    last_name: Optional[str] = Field(description="Author lastname")
    provided_by: Optional[uuid.UUID] = Field(description="UUID of user provided author")
    id: Optional[uuid.UUID] = Field(description="UUID author")

class CreateAuthorForm(BaseModel):
    """Used in author creation """

    name: str = Field(description="Author name")
    surname: str = Field(description="Author surname")
    last_name: str = Field(description="Author lastname")

class RegisterForm(BaseModel):
    username: str = Field(description="Username")
    password: str = Field(description="Password")


class LoginForm(BaseModel):
    username: str = Field(description="Username")
    password: str = Field(description="Password")


class CreateTextForm(BaseModel):
    text: str = Field(description="Text content")
    author_id: uuid.UUID = Field(description="UUID of the author")
    genre_name: str = Field(description="Genre name")


class PredictNearestRequest(BaseModel):
    text: str = Field(description="Text to find nearest matches for")
    k: int = Field(default=5, description="Number of nearest texts to return", ge=1)

class GetMetricsRequest(BaseModel):
    author_id: uuid.UUID = Field(description="UUID of the author")

class StartComputeTaskResponse(BaseModel):
    pass

class GetMetricsTaskResultRequest(BaseModel):
    pass