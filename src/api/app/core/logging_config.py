import logging
import os
import sys
import warnings
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import structlog

# конфиг uvicorn чтобы он тоже логировался через structlog
UVICORN_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": []},
    "loggers": {
        "uvicorn": {"level": "INFO", "handlers": [], "propagate": True},
        "uvicorn.error": {"level": "INFO", "handlers": [], "propagate": True},
        "uvicorn.access": {"level": "INFO", "handlers": [], "propagate": True},
    },
}


def default_log_dir() -> Path:
    raw = os.getenv("LOG_DIR")
    if raw:
        return Path(raw).expanduser().resolve()
    # src/api/app/core -> app root = parents[3]
    _REPO_ROOT = Path(__file__).resolve().parents[4]
    return _REPO_ROOT / "logs"


def _log_file_path() -> Path:
    service = os.getenv("SERVICE_NAME", "api")
    log_dir = default_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / f"{service}.jsonl"


def suppress_noisy_loggers() -> None:
    """чтобы warning от torch не шли в логи"""
    os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning, module=r"torch\..*")

    quiet = (
        "torch",
        "transformers",
        "transformers.modeling_utils",
        "urllib3",
        "matplotlib",
        "mlflow",
        "fastapi",
        "asyncio",
    )
    for name in quiet:
        logging.getLogger(name).setLevel(logging.WARNING)


def _wire_uvicorn_to_root() -> None:
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True


def configure_logging() -> None:
    suppress_noisy_loggers()

    json_logs = os.getenv("LOG_JSON", "1") == "1"
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    file_handler = TimedRotatingFileHandler(
        filename=_log_file_path(),
        when="midnight",
        backupCount=int(os.getenv("LOG_BACKUP_DAYS", "14")),
        encoding="utf-8",
    )
    file_handler.setLevel(level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer = (
        structlog.processors.JSONRenderer()
        if json_logs
        else structlog.dev.ConsoleRenderer(colors=False)
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=shared_processors + [renderer],
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(file_handler)
    root.addHandler(console_handler)
    root.setLevel(level)

    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    _wire_uvicorn_to_root()

    if os.getenv("LOG_UVICORN_ACCESS", "1") != "1":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
