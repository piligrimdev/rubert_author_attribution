import argparse, os, subprocess, yaml
import random
import uuid
from pathlib import Path
import pandas as pd
import mlflow
from pandas import DataFrame
from razdel import sentenize
import hashlib
from transformers import AutoTokenizer

import json


def _send_dataset_metadata(df: DataFrame) -> DataFrame:
    total_texts = len(df)

    num_authors = df['author'].nunique()

    texts_per_author = df.groupby('author').size().to_dict()

    avg_text_length_per_author = df.groupby('author')['text'].apply(
        lambda x: x.str.len().mean()
    ).to_dict()

    mlflow.log_metric("num_authors", num_authors)
    mlflow.log_metric("total_texts", total_texts)

    for author, count in texts_per_author.items():
        mlflow.log_metric(f"texts_count/{author}", count)

    for author, avg_len in avg_text_length_per_author.items():
        mlflow.log_metric(f"avg_text_length/{author}", avg_len)

    metadata = {
        "num_authors": int(num_authors),
        "total_texts": int(total_texts),
        "texts_per_author": {str(k): int(v) for k, v in texts_per_author.items()},
        "avg_text_length_per_author": {str(k): float(v) for k, v in avg_text_length_per_author.items()}
    }

    excluded_authors = []


    mlflow.log_metric(f"excluded_by_less_than_min_text", len(excluded_authors))

    texts_per_author = df.groupby('author').size().to_dict()
    avg_text_length_per_author = df.groupby('author')['text'].apply(
        lambda x: x.str.len().mean()
    ).to_dict()

    for author, count in texts_per_author.items():
        mlflow.log_metric(f"chunked_texts_count/{author}", count)

    for author, avg_len in avg_text_length_per_author.items():
        mlflow.log_metric(f"chuncked_avg_text_length/{author}", avg_len)



def send_mlflow_df_metadata(
        tracking_uri: str,
        experiment: str,
        run_name: str,
        dataset: DataFrame,
        tokenizer_name: str,
        result_file_name: str
) -> None:

    mlflow.set_tracking_uri(tracking_uri)
    if mlflow.active_run() is None:
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment)
        mlflow.start_run(run_name=run_name)

    _send_dataset_metadata(dataset)
    mlflow.log_param("tokenizer", tokenizer_name)
    mlflow.log_param("result_file_name", result_file_name)
