from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Form, UploadFile
from starlette.responses import Response

from ..core.dependencies import (
    CurrentUserUUID,
    session_dependency,
    allowed_extensions,
)
from ..core.services import (
    author_service,
    metrics_service,
    corpus_import_service,
)
from ..schemas.requests import CreateAuthorForm, GetMetricsRequest, EditAuthorForm
from ..schemas.responses import (
    CorpusImportTaskStatus,
    StartCorpusImportTaskResponse,
    AuthorEditResponse
)

authors_routes = APIRouter(prefix="/authors", tags=["authors"])
log = structlog.get_logger(__name__)

csv_file_dep = Annotated[UploadFile, Depends(allowed_extensions("csv"))]

@authors_routes.get("")
async def get_authors(user_id: CurrentUserUUID, session: session_dependency):
    log.debug("authors.list_requested", user_id=str(user_id))
    return await author_service.list_available(user_id=user_id, session=session)

@authors_routes.get("/generative_enabled")
async def get_generative_enabled_authors(
    user_id: CurrentUserUUID, session: session_dependency
):
    log.debug("authors.list_generative_enables_requested", user_id=str(user_id))
    return await author_service.list_generative_enabled(
        user_id=user_id, session=session
    )

@authors_routes.post("/create")
async def create_author(
    form: CreateAuthorForm, user_id: CurrentUserUUID, session: session_dependency
) -> None:

    log.debug("authors.create_requested", user_id=str(user_id))
    return await author_service.create(form, user_id, session)

@authors_routes.delete("/{author_id}")
async def delete_author(
        author_id: str,
        user_id: CurrentUserUUID,
        session: session_dependency
):
    log.debug("authors.delete_requested", user_id=str(user_id))
    await author_service.delete_author(author_id, user_id, session)
    return Response(status_code=204)

@authors_routes.patch("/{author_id}")
async def edit_author(
        author_id: str,
        form: EditAuthorForm,
        user_id: CurrentUserUUID,
        session: session_dependency
) -> AuthorEditResponse:
    log.debug("authors.edit_requested", user_id=str(user_id))
    return await author_service.edit_author(author_id, form, user_id, session)

@authors_routes.post("/compute_metrics")
async def start_compute_metrics_task_endpoint(
    form: GetMetricsRequest, user_id: CurrentUserUUID, session: session_dependency
) -> None:
    log.debug("authors.metrics_computing_requested", user_id=str(user_id))
    return await metrics_service.start_compute_metrics_task(form, user_id, session)


@authors_routes.get("/compute_metrics/{task_id}")
async def get_compute_metrics_task_results_endpoint(
    task_id: str, user_id: CurrentUserUUID
) -> None:
    log.debug("authors.metrics_computing_task_status_requested", user_id=str(user_id))
    return await metrics_service.get_compute_metrics_results(task_id)


@authors_routes.post("/import_csv")
async def start_corpus_csv_import_endpoint(
    user_id: CurrentUserUUID,
    file: csv_file_dep,
) -> StartCorpusImportTaskResponse:
    log.debug("authors.upload_csv_requested", user_id=str(user_id))
    raw = await file.read()
    return await corpus_import_service.start_import_csv_task(
        raw=raw,
        user_id=user_id,
    )


@authors_routes.get("/import_csv/{task_id}")
async def get_corpus_csv_import_status_endpoint(
    task_id: str, user_id: CurrentUserUUID
) -> CorpusImportTaskStatus:
    log.debug("authors.upload_csv_task_status_requested", user_id=str(user_id))
    return await corpus_import_service.get_import_csv_result(task_id)
