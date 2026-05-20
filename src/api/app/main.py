import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import structlog

from .core.database import *
from .core.dependencies import *
from .core.workers import celery
from .core.services import *
from .core.server import *
from .core.entities import *

from .core.logging_config import configure_logging, default_log_dir

_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / ".env")
load_dotenv()

configure_logging()

log = structlog.get_logger("app.startup")
log.info(
    "app.starting",
    service=os.getenv("SERVICE_NAME", "api"),
    log_dir=str(default_log_dir()),
)

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(api.server.serve())
    loop.run_forever()
