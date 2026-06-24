import os
import mlflow
from mlflow.tracking import MlflowClient
from transformers import BertModel

from ..crud.entities.author import AuthorCRUDDatabaseProvider
from ..crud.entities.text import TextCRUDDatabaseProvider
from ..crud.entities.genre import GenreCRUDDatabaseProvider
from ..crud.entities.user import UserCRUDDatabaseProvider, RoleCRUDDatabaseProvider

from ..models.BERT_model import BertModelProvider
from ..models.bert.prediction_strategies import votes_with_sim_threshold

from ..models.qwen_adapted_model_provider import QwenAdaptedModelProvider

from ..models.mock_model import MockModelProvider

from ..services.author_generation_service import GenerativeService
from ..services.genre_service import GenreService
from ..services.corpus_csv_parse_service import CorpusCsvParseService
from ..services.metrics_service import MetricsService
from ..services.embedding_compare_service import EmbeddingCompareService
from ..services.user_service import UserService
from ..services.author_service import AuthorService
from ..services.text_service import TextService
from ..services.attribute_service import AttributeService
from ..core.metrics import get_active_model_name
from ..services.metrics_service import *


from dotenv import load_dotenv

load_dotenv()

mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
mlflow_registry_uri = os.getenv("MLFLOW_REGISTRY_URI", mlflow_tracking_uri)
mlflow.set_tracking_uri(mlflow_tracking_uri)
mlflow.set_registry_uri(mlflow_registry_uri)

mlflow_client = MlflowClient(
    tracking_uri=mlflow_tracking_uri,
    registry_uri=mlflow_registry_uri,
)

use_bert = int(os.getenv("USE_BERT", 0))
use_fasttext = int(os.getenv("USE_FASTTEXT", 0))
model = None

if use_bert:
    bert_name = os.getenv("MLFLOW_BERT_MODEL_NAME", '')
    bert_tag = os.getenv("MLFLOW_BERT_MODEL_TAG", '')
    bert_tokenizer_name = os.getenv("TOKENIZER_NAME", '')
    bert_file_path = os.getenv("BERT_FILE_PATH", '')
    if bert_name:
        raw_model = mlflow.pytorch.load_model(f"models:/{bert_name}/{bert_tag}")
        model = BertModelProvider(model=raw_model, tokenizer_model_name=bert_tokenizer_name)
    elif bert_file_path:
        model = BertModelProvider(
            bert_file_path,
            bert_tokenizer_name
        )
elif use_fasttext:
    from ..models.fasttext_model import FasttextModelProvider

    import glob as _glob
    fasttext_name = os.getenv("MLFLOW_FASTTEXT_MODEL_NAME", "fasttext_classifier")
    fasttext_alias = os.getenv("MLFLOW_FASTTEXT_MODEL_ALIAS", "prod")
    local_dir = mlflow.artifacts.download_artifacts(
        artifact_uri=f"models:/{fasttext_name}@{fasttext_alias}",
        dst_path="/tmp/mlflow_fasttext",
    )
    bin_files = _glob.glob(os.path.join(local_dir, "**/*.bin"), recursive=True)
    if not bin_files:
        raise FileNotFoundError(f"No .bin file found in MLflow artifact for {fasttext_name}@{fasttext_alias}")
    model = FasttextModelProvider(bin_files[0])
else:
    model = MockModelProvider()


user_service = UserService(
    UserCRUDDatabaseProvider(),
    RoleCRUDDatabaseProvider(),
    'basic',
    'admin'
)

author_crud = AuthorCRUDDatabaseProvider()
genre_crud = GenreCRUDDatabaseProvider()
text_crud = TextCRUDDatabaseProvider()

genre_service = GenreService(
    genre_crud
)

author_service = AuthorService(
    author_crud,
    user_service,
)

text_service = TextService(
    text_crud,
    genre_crud,
    author_service,
    user_service,
    model,
)

attribute_service = AttributeService(
    model,
    text_service,
    votes_with_sim_threshold,
    model_name=get_active_model_name(),
)

corpus_csv_parse_service = CorpusCsvParseService()

from ..services.corpus_upload_storage import build_corpus_upload_storage_from_env

corpus_upload_storage = build_corpus_upload_storage_from_env()

use_celery = int(os.getenv("USE_CELERY", 0))

from ..services.corpus_import_service import CorpusImportService

if use_celery:
    from celery.result import AsyncResult
    from ..services.metrics_service import metrics_compute
    from ..services.embedding_compare_service import embedding_compare_compute
    from ..services.corpus_import_service import corpus_csv_import

    metrics_service = MetricsService(
        text_service,
        metrics_compute,
        AsyncResult,
    )
    embedding_compare_service = EmbeddingCompareService(
        text_service,
        embedding_compare_compute,
        AsyncResult,
    )
    corpus_import_service = CorpusImportService(
        author_service,
        genre_service,
        text_service,
        user_service,
        corpus_csv_parse_service,
        corpus_upload_storage,
        corpus_csv_import,
        AsyncResult,
    )
else:
    from ..services.mock_worker_provider import create_mock_async_result, MockTaskCache
    from ..services.metrics_service import create_mock_async_metric_compute
    from ..services.embedding_compare_service import create_mock_async_embedding_compare_compute
    from ..services.corpus_import_service import create_mock_async_corpus_csv_import

    task_cache = MockTaskCache()
    compute_metrics_method = create_mock_async_metric_compute(task_cache)
    compute_embedding_compare_method = create_mock_async_embedding_compare_compute(task_cache)
    corpus_csv_import_method = create_mock_async_corpus_csv_import(task_cache)
    get_async_result = create_mock_async_result(task_cache)

    metrics_service = MetricsService(
        text_service,
        compute_metrics_method,
        get_async_result,
    )
    embedding_compare_service = EmbeddingCompareService(
        text_service,
        compute_embedding_compare_method,
        get_async_result,
    )
    corpus_import_service = CorpusImportService(
        author_service,
        genre_service,
        text_service,
        user_service,
        corpus_csv_parse_service,
        corpus_upload_storage,
        corpus_csv_import_method,
        get_async_result,
    )

SYSTEM_PROMPT = (
    "Ты — стилист текста. Перепиши данный нейтральный текст в стиле автора, "
    "сохранив смысл, но изменив манеру изложения, лексику и интонацию."
)

use_qwen = int(os.getenv("USE_QWEN", 0))
generative_model = None
if use_qwen:
    generative_model = QwenAdaptedModelProvider(
        base_model_name=os.getenv("QWEN_BASE_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
        registered_name=os.getenv("MLFLOW_QWEN_MODEL_NAME", "qwen_lora_stylizer"),
        alias=os.getenv("MLFLOW_QWEN_MODEL_ALIAS", "prod"),
        system_prompt=SYSTEM_PROMPT,
    )

generative_service = GenerativeService(generative_model)
