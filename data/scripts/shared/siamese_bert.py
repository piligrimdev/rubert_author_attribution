import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModel


class SiameseBERT(nn.Module):

    def __init__(self, model_name: str = 'DeepPavlov/rubert-base-cased',
                 dropout: float = 0.2,
                 hidden_head_size: int = 512,
                 embedding_dim: int = 256):
        super().__init__()

        self.bert = AutoModel.from_pretrained(model_name)
        hidden_size = self.bert.config.hidden_size

        self.projection = nn.Sequential(
            nn.Linear(hidden_size, hidden_head_size),
            nn.LayerNorm(hidden_head_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_head_size, embedding_dim)
        )

    def encode(self, input_ids: torch.Tensor,
           attention_mask: torch.Tensor) -> torch.Tensor:
        out = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        token_embeddings = out.last_hidden_state

        mask_expanded = attention_mask.unsqueeze(-1).float()

        sum_embeddings = (token_embeddings * mask_expanded).sum(dim=1)

        token_counts = mask_expanded.sum(dim=1).clamp(min=1e-9)

        pooled = sum_embeddings / token_counts

        projected = self.projection(pooled)

        _result = F.normalize(projected, p=2, dim=-1)

        return _result

    def forward(self, input_ids, attention_mask):
        return self.encode(input_ids, attention_mask)
