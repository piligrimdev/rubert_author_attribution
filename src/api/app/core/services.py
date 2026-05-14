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
from ..services.metrics_service import MetricsService
from ..services.user_service import UserService
from ..services.author_service import AuthorService
from ..services.text_service import TextService
from ..services.attribute_service import AttributeService
from ..services.metrics_service import *


from dotenv import load_dotenv

load_dotenv()

mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
mlflow.set_tracking_uri(mlflow_tracking_uri)

mlflow_client = MlflowClient()

use_bert = int(os.getenv("USE_BERT", 0))
model=None
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
else:
    model = MockModelProvider()


user_service = UserService(
    UserCRUDDatabaseProvider(),
    RoleCRUDDatabaseProvider(),
    'basic',
    'admin'
)

author_service = AuthorService(
    AuthorCRUDDatabaseProvider(),
    user_service
)

text_service = TextService(
    TextCRUDDatabaseProvider(),
    GenreCRUDDatabaseProvider(),
    author_service,
    user_service,
    model,
)

attribute_service = AttributeService(model, text_service, votes_with_sim_threshold)
task_cache = MockTaskCache()

metrics_service = MetricsService(
    text_service,
    mock_metrics_compute,
    task_cache
)

SYSTEM_PROMPT = (
    "Ты — стилист текста. Перепиши данный нейтральный текст в стиле автора, "
    "сохранив смысл, но изменив манеру изложения, лексику и интонацию."
)

# generative_model = QwenAdaptedModelProvider(
#     'Qwen/Qwen2.5-7B-Instruct',
#     '/Users/pgdev/PycharmProjects/diplomm/models/qwn',
#     SYSTEM_PROMPT
# )

generative_service = GenerativeService(
    None
)
