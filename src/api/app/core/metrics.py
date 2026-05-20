import os
import time
from prometheus_client import Counter, Histogram, start_http_server
from prometheus_fastapi_instrumentator import Instrumentator

from ..schemas.responses import AttributionProba, VotesResponse

ATTRIBUTION_TOTAL = Counter(
    "model_attribution_total",
    "Attribution predictions",
    ["model", "outcome"],  # predicted if > threshold | abstain if not
)

ATTRIBUTION_LATENCY = Histogram(
    "model_attribution_seconds",
    "Attribution latency",
    ["model"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30),
)

ATTRIBUTION_TOP1_CONFIDENCE = Histogram(
    "model_attribution_top1_confidence",
    "Top-1 confidence (VotesResponse.confidence or max proba)",
    ["model"],
    buckets=(0.1, 0.2, 0.3, 0.5, 0.7, 0.85, 0.95, 1.0),
)


CELERY_TASK_TOTAL = Counter(
    "celery_task_total",
    "Celery tasks finished",
    ["task_name", "status"],
)

CELERY_TASK_DURATION = Histogram(
    "celery_task_seconds",
    "Celery task duration",
    ["task_name", "status"],
    buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60, 120, 300, 600),
)

_celery_task_started_at: dict[str, float] = {}


def get_active_model_name() -> str:
    if int(os.getenv("USE_BERT", "0")):
        return os.getenv("MLFLOW_BERT_MODEL_NAME") or "bert"
    if int(os.getenv("USE_FASTTEXT", "0")):
        return os.getenv("MLFLOW_FASTTEXT_MODEL_NAME") or "fasttext"
    if int(os.getenv("USE_QWEN", "0")):
        return os.getenv("MLFLOW_QWEN_MODEL_NAME") or "qwen"
    return "mock"


def setup_http_metrics(app) -> None:
    if os.getenv("METRICS_ENABLED", "1") != "1":
        return

    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        excluded_handlers=["/metrics", "/health"],
    ).instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=False,
    )


def record_attribution(
    result: VotesResponse | list[AttributionProba],
    *,
    model: str,
    duration_seconds: float,
) -> None:
    ATTRIBUTION_LATENCY.labels(model=model).observe(duration_seconds)

    if isinstance(result, VotesResponse):
        outcome = "abstain" if result.predicted is None else "predicted"
        ATTRIBUTION_TOTAL.labels(model=model, outcome=outcome).inc()
        ATTRIBUTION_TOP1_CONFIDENCE.labels(model=model).observe(result.confidence)
        return

    if isinstance(result, list) and result:
        top = max(result, key=lambda x: x.proba)
        ATTRIBUTION_TOTAL.labels(model=model, outcome="predicted").inc()
        ATTRIBUTION_TOP1_CONFIDENCE.labels(model=model).observe(top.proba)
        return

    ATTRIBUTION_TOTAL.labels(model=model, outcome="abstain").inc()


def observe_celery_task_start(task_id: str) -> None:
    _celery_task_started_at[task_id] = time.perf_counter()


def observe_celery_task_end(task_id: str, task_name: str, status: str) -> None:
    started = _celery_task_started_at.pop(task_id, None)
    duration = time.perf_counter() - started if started is not None else 0.0
    CELERY_TASK_TOTAL.labels(task_name=task_name, status=status).inc()
    CELERY_TASK_DURATION.labels(task_name=task_name, status=status).observe(duration)


def setup_celery_metrics() -> None:
    if os.getenv("METRICS_ENABLED", "1") != "1":
        return
    port = int(os.getenv("CELERY_METRICS_PORT", "8001"))
    start_http_server(port)


def connect_celery_signals() -> None:
    from celery import signals

    @signals.task_prerun.connect
    def _on_prerun(task_id=None, task=None, **kwargs):
        if task_id:
            observe_celery_task_start(task_id)

    @signals.task_postrun.connect
    def _on_postrun(task_id=None, task=None, state=None, **kwargs):
        if task_id and task is not None:
            observe_celery_task_end(task_id, task.name, state or "UNKNOWN")

    @signals.task_failure.connect
    def _on_failure(task_id=None, task=None, **kwargs):
        if task_id and task is not None:
            observe_celery_task_end(task_id, task.name, "FAILURE")

    @signals.worker_ready.connect
    def _on_worker_ready(**kwargs):
        setup_celery_metrics()
