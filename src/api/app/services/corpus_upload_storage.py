import os
import uuid
from pathlib import Path
from typing import Protocol
import structlog

logger = structlog.get_logger(__name__)

class CorpusUploadStorage(Protocol):
    """Нужно для общения файлами между api и celery"""
    def put(self, raw: bytes) -> str: ...
    def read(self, key: str) -> bytes: ...
    def delete(self, key: str) -> None: ...


class LocalCorpusUploadStorage:
    """Для ручного запуска api/celery или общего volume в docker compse"""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        logger.debug("csv_local_storage.init.created_directory", base_dir=self.base_dir)

    def _path(self, key: str) -> Path:
        return Path(self.base_dir) / key

    def put(self, raw: bytes) -> str:
        key = f"corpus_import_{uuid.uuid4().hex}.csv"
        self._path(key).write_bytes(raw)
        logger.debug("csv_local_storage.put.saved")
        return key

    def read(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def delete(self, key: str) -> None:
        try:
            self._path(key).unlink(missing_ok=True)
            logger.debug("csv_local_storage.delete.deleted")
        except OSError as err:
            logger.error("csv_local_storage.delete.error", error=err)
            pass


class S3CorpusUploadStorage:
    def __init__(
        self,
        bucket: str,
        prefix: str = "corpus_import",
        endpoint_url: str | None = None,
        region_name: str | None = None,
    ):
        self.bucket = bucket
        self.prefix = prefix.strip("/")
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self._client = None

    def _get_client(self):
        if self._client is None:
            import boto3  # если нет в dev/CLI

            self._client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                region_name=self.region_name,
            )
        return self._client

    def _key_path(self, key: str) -> str:
        return f"{self.prefix}/{key}" if self.prefix else key

    def put(self, raw: bytes) -> str:
        key = f"{uuid.uuid4().hex}.csv"
        self._get_client().put_object(
            Bucket=self.bucket,
            Key=self._key_path(key),
            Body=raw,
            ContentType="text/csv",
        )
        return key

    def read(self, key: str) -> bytes:
        resp = self._get_client().get_object(
            Bucket=self.bucket, Key=self._key_path(key)
        )
        return resp["Body"].read()

    def delete(self, key: str) -> None:
        try:
            self._get_client().delete_object(
                Bucket=self.bucket, Key=self._key_path(key)
            )
        except Exception:
            pass


def build_corpus_upload_storage_from_env() -> CorpusUploadStorage:
    backend = (os.getenv("CORPUS_UPLOAD_STORAGE") or "local").lower()

    if backend == "s3":
        bucket = os.getenv("CORPUS_S3_BUCKET") or os.getenv("MLFLOW_BUCKET")
        if not bucket:
            raise RuntimeError(
                "S3 storage selected but neither CORPUS_S3_BUCKET nor MLFLOW_BUCKET is set"
            )
        return S3CorpusUploadStorage(
            bucket=bucket,
            prefix=os.getenv("CORPUS_S3_PREFIX", "corpus_import"),
            endpoint_url=(
                os.getenv("S3_ENDPOINT_URL")
                or os.getenv("MLFLOW_S3_ENDPOINT_URL")
            ),
            region_name=os.getenv("AWS_DEFAULT_REGION"),
        )

    import tempfile

    base_dir = os.getenv("CORPUS_IMPORT_DIR") or tempfile.gettempdir()
    return LocalCorpusUploadStorage(base_dir=base_dir)
