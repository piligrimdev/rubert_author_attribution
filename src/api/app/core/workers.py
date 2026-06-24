import os
from celery import Celery

from dotenv import load_dotenv

load_dotenv()

from .logging_config import configure_logging

configure_logging()

celery = Celery(__name__)

celery.conf.broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379")

from .database import *
from .services import *
from .entities import *

from ..services import corpus_import_service
from ..services import metrics_service
from ..services import embedding_compare_service

from .metrics import connect_celery_signals

connect_celery_signals()

