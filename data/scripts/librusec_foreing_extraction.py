import argparse
from datasets import load_dataset
import pandas as pd
from transformers import AutoTokenizer

from shared.chunks_by_tokens import split_text_to_chunks
from shared.send_df_meta_to_mlflow import send_mlflow_df_metadata

def main():

    p = argparse.ArgumentParser()
    p.add_argument("--tokenizer", default="DeepPavlov/rubert-base-cased")
    p.add_argument("--result_csv_name", default="librusec.csv")
    p.add_argument('--authors', nargs='+')

    p.add_argument("--use_mlflow", action="store_true", default=True)
    p.add_argument("--mlflow-tracking-uri", default="http://localhost:2000")
    p.add_argument("--run_name", default="preprocessing_librusec_dataset")
    args = p.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)

    dataset = load_dataset("NejimakiTori/literature_sum", split="train")
    df = dataset.to_pandas()

    authors_list = args.authors
    if not authors_list:
        authors_list = ['Кристи', 'Брэдбери', 'Дойл','Верн', 'Роулинг', 'Мопассан']

    ok_authors = df[df.author.isin(authors_list)]

    ok_authors['text'] = ok_authors['text'].apply(lambda x: x[0])

    split_df = split_text_to_chunks(ok_authors, tokenizer)

    split_df.to_csv(args.result_csv_name)

    if args.use_mlflow:
        if not args.mlflow_tracking_uri:
            raise RuntimeError("You need to specify mlflow tracking uri")
        send_mlflow_df_metadata(
            args.mlflow_tracking_uri,
            'librusec_exctraction',
            args.run_name,
            split_df,
            args.tokenizer,
            args.result_csv_name,
        )

if __name__ == "__main__":
    main()

