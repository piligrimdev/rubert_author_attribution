import structlog
import torch
from torch import nn, autocast
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

from .abstract_model_provider import AbstractModelProvider

logger = structlog.get_logger(__name__)


class BertModelProvider(AbstractModelProvider):
    is_embedder = True

    def __init__(
            self,
            path_to_pretrained_model: str = "",
            tokenizer_model_name: str = "",
            max_emb_len=256,
            model = None,
    ):

        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_model_name)

        if model:
            self.model = model
            self.model.eval()

        self.max_emb_len = max_emb_len

    def predict(
            self, text: str, k_nearest: int = 5,
    ) -> list[dict[str, float]]:
        raise NotImplementedError


    def generate_embedding(self, text: str) -> list:
        if not self.model:
            logger.warning("bert.embedding.no_model_provided")
            return [0]*self.max_emb_len

        with torch.no_grad():
            enc = self.tokenizer(
                text, max_length=self.max_emb_len,
                padding=True, truncation=True,  # padding=True = dynamic padding до max в батче
                return_tensors='pt'
            )
            with autocast(device_type='cuda', enabled=False, dtype=torch.float16):  # fp16 и при инференсе
                embs = self.model.encode(
                    enc['input_ids'],
                    enc['attention_mask']
                ).float().cpu().numpy()
                result = embs.tolist()
                logger.info("bert.embedding.generated_embedding")
                return result
