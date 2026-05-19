import os
from celery import Celery

from dotenv import load_dotenv

load_dotenv()

celery = Celery(__name__)

celery.conf.broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379")

from .database import *
from .services import *
from .entities import *

from ..services import corpus_import_service
from ..services import metrics_service

