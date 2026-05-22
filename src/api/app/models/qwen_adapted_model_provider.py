import os

import mlflow
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from .abstract_generative_model_provier import AbstractGenerativeModelProvider


class QwenAdaptedModelProvider(AbstractGenerativeModelProvider):
    def __init__(
        self,
        base_model_name: str,
        registered_name: str,
        alias: str = "prod",
        system_prompt: str | None = None,
        cache_dir: str = "/tmp/mlflow_qwen_lora",
    ):
        super().__init__()
        if not torch.cuda.is_available():
            raise RuntimeError(
                "QwenAdaptedModelProvider requires a CUDA device. "
                "Set USE_QWEN=0 on CPU-only deployments."
            )

        self.system_prompt = system_prompt

        os.makedirs(cache_dir, exist_ok=True)
        adapter_dir = mlflow.artifacts.download_artifacts(
            artifact_uri=f"models:/{registered_name}@{alias}",
            dst_path=cache_dir,
        )

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        self.model = PeftModel.from_pretrained(base_model, adapter_dir).eval()
        self.tokenizer = AutoTokenizer.from_pretrained(adapter_dir, trust_remote_code=True)

    async def generate(
        self,
        text: str,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
        rep_penalty: float = 1.1,
    ) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text},
        ]
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=rep_penalty,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        new_tokens = output[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
