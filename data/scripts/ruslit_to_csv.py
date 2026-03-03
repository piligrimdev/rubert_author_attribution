import argparse
import os
import re
import pandas as pd
from pathlib import Path
from transformers import AutoTokenizer

from shared.chunks_by_tokens import split_text_to_chunks
from shared.send_df_meta_to_mlflow import send_mlflow_df_metadata

def extract_author_from_filename(filepath):
    stem = Path(filepath).stem
    return stem.split('_')[0]

def extract_author_from_folder(filepath):
    return Path(filepath).parent.name

def load_books(root_dir):
    records = []
    for path in Path(root_dir).rglob('*.txt'):
        text = path.read_text(encoding='utf-8', errors='ignore')
        author = extract_author_from_filename(path)
        records.append({
            'author': author,
            'title': path.stem,
            'text': text,
            'filepath': str(path)
        })
    return pd.DataFrame(records)

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)          # лишние пробелы
    text = re.sub(r'[^\w\s\.,!?;:\-—«»"\'()]', '', text)  # мусорные символы
    text = re.sub(r'\d{2,}', '', text)        # номера страниц и т.п.
    return text.strip()


def main():

    p = argparse.ArgumentParser()
    p.add_argument("--tokenizer", default="DeepPavlov/rubert-base-cased")
    p.add_argument("--result_csv_name", default="ruslit.csv")
    p.add_argument("--path_to_corpus")
    p.add_argument("--use_mlflow", action="store_true")
    p.add_argument("--mlflow-tracking-uri", default="http://localhost:2000")
    p.add_argument("--run_name", default="preprocessing_ruslit_dataset")
    args = p.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)

    df = load_books(args.path_to_corpus)

    df_chunks = split_text_to_chunks(df, tokenizer, author_col='author', text_col='text')

    print(df_chunks.groupby('author').size())  # баланс классов

    df_chunks['text'] = df_chunks['text'].apply(clean_text)
    df_chunks = df_chunks[df_chunks['text'].str.len() > 100]  # убрать пустые

    df_chunks.to_csv(args.result_csv_name, index=False, encoding='utf-8-sig')

    print(f"Всего чанков: {len(df_chunks)}")

    if args.use_mlflow:
        if not args.mlflow_tracking_uri:
            raise RuntimeError("You need to specify mlflow tracking uri")
        send_mlflow_df_metadata(
            args.mlflow_tracking_uri,
            'ruslit_parser',
            args.run_name,
            df_chunks,
            args.tokenizer,
            args.result_csv_name,
        )


if __name__ == "__main__":
    main()
