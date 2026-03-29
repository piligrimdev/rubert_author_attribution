import argparse
import os

import mlflow.pytorch
import torch
from dotenv import load_dotenv
from transformers import AutoTokenizer


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--mlflow-tracking-uri", default="http://localhost:2000")
    p.add_argument("--model-name", required=True, help="Имя модели в MLflow Registry, например rubert-author-attribution")
    p.add_argument("--text", required=True, help="Текст для получения эмбеддинга")
    p.add_argument("--max-len", type=int, default=256)
    return p.parse_args()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mlflow-tracking-uri", default="http://localhost:2000")
    p.add_argument("--model-name", required=True, help="Имя модели в MLflow Registry, например rubert-author-attribution")
    p.add_argument("--text", required=True, help="Текст для получения эмбеддинга")
    p.add_argument("--max-len", type=int, default=256)
    args = p.parse_args()


    mlflow.set_tracking_uri(args.mlflow_tracking_uri)
    print(f"Загружаю модель: {args.model_name}")
    model = mlflow.pytorch.load_model(f"models:/{args.model_name}/latest")
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")
    tokens = tokenizer(
        args.text,
        max_length=args.max_len,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )

    with torch.no_grad():
        embedding = model(tokens["input_ids"], tokens["attention_mask"])

    print(f"Эмбеддинг (dim={embedding.shape[-1]}):")
    print(embedding[0].numpy())


if __name__ == "__main__":
    main()
