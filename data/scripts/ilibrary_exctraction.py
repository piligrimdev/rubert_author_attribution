import pandas as pd
from transformers import AutoTokenizer
import argparse

from shared.chunks_by_tokens import split_text_to_chunks
from shared.send_df_meta_to_mlflow import send_mlflow_df_metadata

def main():

    p = argparse.ArgumentParser()
    p.add_argument("--tokenizer", default="DeepPavlov/rubert-base-cased")
    p.add_argument("--result_csv_name", default="ilibrary_chunked.csv")
    p.add_argument("--path_to_corpus")
    p.add_argument('--authors', nargs='+')
    p.add_argument('--books', nargs='+')
    p.add_argument("--use_mlflow", action="store_true")
    p.add_argument("--mlflow-tracking-uri", default="http://localhost:2000")
    p.add_argument("--run_name", default="preprocessing_ilibrary_dataset")
    args = p.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)

    new_df = pd.read_csv(args.path_to_corpus)
    new_df.columns=["author", "title", "url", 'text']
    new_df.drop(columns=['url',], inplace=True)

    ok_authors_list = args.authors
    if not ok_authors_list:
        ok_authors_list = ['Скотт', 'Андерсен', 'Белинский', 'Гете', 'Гончаров', 'Грибоедов', 'Гумилев', 'Дефо', 'Замятин', 'Лондон', 'Мережковский', 'Платонов', 'Шекспир', 'Гайдар', 'Грин', 'Куприн', 'Толстой А.К.']

    ok_authors = pd.DataFrame()
    for name in ok_authors_list:
        part = new_df[new_df['author'].str.contains(name)]
        if not part.empty:
            print(part.iloc[0]['author'])
            ok_authors = pd.concat([ok_authors, part])
    df_to_chunk = ok_authors

    # book_list = ['Униженные', 'подполья', 'муж' 'Смерть', 'Хаджи-Мурат', 'Юность']
    book_list = args.books
    if book_list:
        ok_books = pd.DataFrame()
        for name in book_list:
            part = ok_authors[new_df['title'].str.contains(name)]
            if not part.empty:
                print(part.iloc[0]['author'])
                ok_books = pd.concat([ok_books, part])
        df_to_chunk = ok_books

    df_chunks = split_text_to_chunks(df_to_chunk, tokenizer)

    df_chunks.to_csv(args.result_csv_name)

    if args.use_mlflow:
        if not args.mlflow_tracking_uri:
            raise RuntimeError("You need to specify mlflow tracking uri")
        send_mlflow_df_metadata(
            args.mlflow_tracking_uri,
            'ilibrary_exctraction',
            args.run_name,
            df_chunks,
            args.tokenizer,
            args.result_csv_name,
        )

if __name__ == "__main__":
    main()
