import asyncio
import uuid
from pathlib import Path
from typing import Callable, Optional
import structlog
from celery import states as celery_states
from fastapi import HTTPException

from .user_service import UserService
from ..core.workers import celery
from ..schemas.responses import (
    CorpusCsvImportResult,
    CorpusImportTaskStatus,
    StartCorpusImportTaskResponse,
)
from .author_service import AuthorService
from .corpus_csv_parse_service import CorpusCsvParseError, CorpusCsvParseService
from .genre_service import GenreService
from .mock_worker_provider import MockTaskCache, TaskData
from .text_service import TextService

from .corpus_upload_storage import CorpusUploadStorage

logger = structlog.get_logger(__name__)

def parse_author_name(full_name: str) -> tuple[str, str, str]:
    return full_name, "", ""


class CorpusImportService:
    def __init__(
        self,
        author_service: AuthorService,
        genre_service: GenreService,
        text_service: TextService,
        user_service: UserService,
        parse_service: CorpusCsvParseService,
        upload_storage: CorpusUploadStorage,
        on_import_csv: Optional[Callable],
        async_result_fn: Optional[Callable],
    ):
        self.author_service = author_service
        self.genre_service = genre_service
        self.text_service = text_service
        self.user_service = user_service

        self.parse_service = parse_service
        self.upload_storage = upload_storage
        self.on_import_csv = on_import_csv
        self.async_result_fn = async_result_fn


    async def import_dataframe(
        self,
        df,
        user_id,
        session,
        progress_cb: Optional[Callable[[int, int], None]] = None,
    ) -> CorpusCsvImportResult:
        """Общая бизнес-логика импорта: используется из CLI, Celery и mock-обёртки."""
        total = len(df)
        added = 0
        skipped_empty = 0
        errors = 0

        author_cache: dict[str, object] = {}
        genre_cache: dict[str, object] = {}

        user_obj = await self.user_service.get_user_by_id(user_id, session)
        is_admin = await self.user_service.is_user_admin(user_obj)

        logger.debug("csv_parsing.parsing.is_user_admin", is_user_admin=is_admin, user_obj=user_obj)

        for processed, (_, row) in enumerate(df.iterrows(), start=1):
            try:
                author_str = str(row["author"]).strip()
                text_content = str(row["text"]).strip()
                genre_col = str(row["source_type"]).strip()

                if not all([author_str, text_content, genre_col]):
                    logger.debug("csv_parsing.parsing.skipped_row_due_to_missing_colums", row_idx=processed)
                    skipped_empty += 1
                    continue

                genre = genre_cache.get(genre_col)
                if not genre:
                    if is_admin:
                        genre = await self.genre_service.get_or_create_entity(
                            genre_col, session=session
                        )
                        logger.info("csv_parsing.parsing.admin_created_genre_from_csv", row_idx=processed)
                    else:
                        genre = await self.genre_service.get_by_name_entity(genre_col, session=session)
                        logger.info("csv_parsing.parsing.user_got_genre_from_db", row_idx=processed)
                    genre_cache[genre_col] = genre

                author = author_cache.get(author_str)
                if author is None:
                    name, surname, last_name = parse_author_name(author_str)
                    author = await self.author_service.get_or_create_entity(
                        name, surname, last_name, user_id, session
                    )
                    author_cache[author_str] = author

                await self.text_service.add_text_entity(
                    text=text_content,
                    author=author,
                    genre=genre,
                    user_id=user_id,
                    session=session,
                )
                logger.info("csv_parsing.parsing.text_from_csv_added", row_idx=processed)
                added += 1
            except Exception as e:
                logger.error("csv_parsing.parsing.error_on_processing_row", error=e)
                errors += 1
            finally:
                if progress_cb is not None:
                    progress_cb(processed, total)

        logger.info("csv_parsing.parsing.finished",
                    added=added,
                    skipped_empty=skipped_empty,
                    errors=errors
        )
        return CorpusCsvImportResult(
            added=added,
            skipped_empty=skipped_empty,
            errors=errors
        )

    async def import_from_file(
        self,
        file_path: str,
        user_id,
        session,
        progress_cb: Optional[Callable[[int, int], None]] = None,
    ) -> CorpusCsvImportResult:
        logger.debug("csv_parsing.import_from_file.reading_file_raw")
        raw = Path(file_path).read_bytes()
        df = self.parse_service.prepare_dataframe(raw)
        return await self.import_dataframe(
            df,
            user_id=user_id,
            session=session,
            progress_cb=progress_cb,
        )

    async def import_from_storage(
        self,
        key: str,
        user_id,
        session,
        progress_cb: Optional[Callable[[int, int], None]] = None,
    ) -> CorpusCsvImportResult:
        """Читает CSV из upload-хранилища (для запуска внутри Celery)."""
        logger.debug("csv_parsing.import_from_file.reading_file_from_storage")
        raw = self.upload_storage.read(key)
        df = self.parse_service.prepare_dataframe(raw)
        return await self.import_dataframe(
            df,
            user_id=user_id,
            session=session,
            progress_cb=progress_cb,
        )

    async def start_import_csv_task(
        self,
        raw: bytes,
        user_id: uuid.UUID,
    ) -> StartCorpusImportTaskResponse:
        """Складывает CSV в upload-хранилище и ставит задачу.

        В dev по умолчанию это локальный каталог, который монтируется в оба
        контейнера (web + worker) как shared volume. В prod —
        Yandex S3 (``CORPUS_UPLOAD_STORAGE=s3``). Контракт задачи —
        ``(user_id, key)``, opaque-ключ хранилища.
        """
        if self.on_import_csv is None:
            logger.error("csv_parsing.start_import_csv_task.no_method_provided_error")
            raise HTTPException(
                status_code=503,
                detail="No method provided for .csv parsing",
            )

        try:
            self.parse_service.prepare_dataframe(raw)
        except CorpusCsvParseError as exc:
            logger.error("csv_parsing.start_import_csv_task.prepare_error", error=exc)
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        logger.debug("csv_parsing.start_import_csv_task.file_uploading_to_storage")
        key = self.upload_storage.put(raw)
        logger.debug("csv_parsing.start_import_csv_task.file_uploaded_to_storage")

        try:
            task_id = await self.on_import_csv(str(user_id), key)
            logger.info("csv_parsing.start_import_csv_task.csv_proccessing_task_created", task_id=task_id)
        except Exception as e:
            logger.error("csv_parsing.start_import_csv_task.prepare_error", error=e)
            self.upload_storage.delete(key)
            logger.debug("csv_parsing.start_import_csv_task.file_deleted_from_storage")
            raise

        return StartCorpusImportTaskResponse(task_id=str(task_id))

    async def get_import_csv_result(self, task_id: str) -> CorpusImportTaskStatus:
        if self.async_result_fn is None:
            logger.error("csv_parsing.get_import_csv_result.no_task_status_checking_method_provided",)
            raise HTTPException(
                status_code=503,
                detail="No task status checking method provided",
            )

        result = self.async_result_fn(task_id)
        if result is None:
            logger.error("csv_parsing.get_import_csv_result.task_not_found", task_id=task_id)
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


        status = getattr(result, "status", None) or getattr(result, "state", None)
        info = getattr(result, "info", None)
        payload = getattr(result, "result", None)

        logger.debug("csv_parsing.get_import_csv_result.task_has_status", task_id=task_id, status=status)

        if status == celery_states.SUCCESS:
            logger.debug("csv_parsing.get_import_csv_result.task_completed", task_id=task_id)
            return CorpusImportTaskStatus(
                task_id=str(task_id),
                status=status,
                progress=100.0,
                result=CorpusCsvImportResult.model_validate(payload),
            )

        if status == celery_states.FAILURE:
            logger.error("csv_parsing.get_import_csv_result.task_failed", task_id=task_id)
            return CorpusImportTaskStatus(
                task_id=str(task_id),
                status=status,
                progress=None,
                error=str(payload) if payload is not None else "Task failed",
            )

        progress: Optional[float] = None
        meta = info if isinstance(info, dict) else None
        if meta is None and isinstance(payload, dict):
            meta = payload
        if meta is not None and "percent" in meta:
            try:
                progress = float(meta["percent"])
            except (TypeError, ValueError):
                logger.error("csv_parsing.get_import_csv_result.failed_to_fetch_progress", task_id=task_id)
                progress = None

        return CorpusImportTaskStatus(
            task_id=str(task_id),
            status=status or celery_states.PENDING,
            progress=progress,
        )


@celery.task(bind=True, name="corpus_csv_import")
def corpus_csv_import_celery(self, user_id: str, key: str) -> dict:
    """Прогон импорта в воркере с ленивым DI сервисов из ``core.services``.

    ``key`` — opaque-ключ ``upload_storage`` (имя файла в shared volume для
    dev, либо S3-ключ для prod). Воркер сам читает CSV и удаляет за собой.
    """
    logger.debug("csv_parsing.import_task_started")
    from ..core.database import database
    from ..core.services import corpus_import_service as _service

    def progress_cb(current: int, total: int) -> None:
        percent = (current * 100.0 / total) if total else 0.0
        self.update_state(
            state="PROGRESS",
            meta={"current": current, "total": total, "percent": percent},
        )

    uid = uuid.UUID(user_id)

    async def _run() -> CorpusCsvImportResult:
        with database.get_sync_session() as session:
            return await _service.import_from_storage(
                key=key,
                user_id=uid,
                session=session,
                progress_cb=progress_cb,
            )

    try:
        result = asyncio.run(_run())
        result =  result.model_dump()
        logger.debug("csv_parsing.import_task_finished")
        return result
    finally:
        _service.upload_storage.delete(key)
        logger.debug("csv_parsing.file_deleted_from_storage")


async def corpus_csv_import(user_id: str, key: str) -> str:
    """Делегат в Celery — структурно совпадает с ``metrics_compute``."""
    logger.debug("csv_parsing.task_delayed")
    task = corpus_csv_import_celery.delay(user_id, key)
    return task.id


def create_mock_async_corpus_csv_import(mock_cache: MockTaskCache) -> Callable:
    """Mock-обёртка для запуска без Celery: импорт выполняется синхронно."""

    async def mock_corpus_csv_import(
        user_id: str, key: str
    ) -> uuid.UUID:
        from ..core.database import database
        from ..core.services import corpus_import_service as _service

        task_uuid = uuid.uuid4()

        logger.debug("csv_parsing.mock_import_task_started")
        try:
            uid = uuid.UUID(user_id)
            with database.get_sync_session() as session:
                result = await _service.import_from_storage(
                    key=key,
                    user_id=uid,
                    session=session,
                )
            task_data = TaskData(
                id=task_uuid,
                status=celery_states.SUCCESS,
                result=result.model_dump(),
            )
        except Exception as exc:
            task_data = TaskData(
                id=task_uuid,
                status=celery_states.FAILURE,
                result=str(exc),
            )
        finally:
            _service.upload_storage.delete(key)
            logger.debug("csv_parsing.file_deleted_from_storage")

        mock_cache.put(task_uuid, task_data)
        logger.debug("csv_parsing.mock_import_task_finished")
        return task_uuid

    return mock_corpus_csv_import
