import mlflow
import pandas as pd
import argparse
from shared.send_df_meta_to_mlflow import _send_dataset_metadata


def balance_authors(df: pd.DataFrame,
                    author_col: str = 'author',
                    min_fragments: int = 50,
                    max_fragments: int = 500,
                    random_state: int = 42) -> pd.DataFrame:
    balanced_parts = []
    excluded_authors = []

    for author, group in df.groupby(author_col):
        n = len(group)

        if n < min_fragments:
            excluded_authors.append((author, n))
            continue

        if n > max_fragments:
            group = group.sample(n=max_fragments, random_state=random_state)

        balanced_parts.append(group)

    if excluded_authors:
        print(f"Excluded authors:")
        for author, count in excluded_authors:
            print(f"\t{author}: {count} chunks")

    balanced_df = pd.concat(balanced_parts, ignore_index=True)

    print(f"Balanced authors: {balanced_df['author'].nunique()}")

    return balanced_df

def main():

    p = argparse.ArgumentParser()
    p.add_argument("--result_csv_name", default="balanced_lit.csv")
    p.add_argument("--path_to_corpus")

    p.add_argument("--use_mlflow", action="store_true")
    p.add_argument("--mlflow-tracking-uri", default="http://localhost:2000")
    p.add_argument("--random_state", default=42, type=int)
    p.add_argument("--min_chunks", default=400, type=int)
    p.add_argument("--max_chunks", default=3000, type=int)
    p.add_argument("--run_name", default="balancing_authors")
    args = p.parse_args()

    df = pd.read_csv(args.path_to_corpus)

    balanced_df = balance_authors(
        df,
        min_fragments=args.min_chunks
        , max_fragments=args.max_chunks,
        random_state=args.random_state
    )

    balanced_df.to_csv(args.result_csv_name, index=False)

    if args.use_mlflow:
        if not args.mlflow_tracking_uri:
            raise RuntimeError("You need to specify mlflow tracking uri")

        mlflow.set_tracking_uri(args.mlflow_tracking_uri)
        if mlflow.active_run() is None:
            mlflow.set_experiment('balancing_authors')
            mlflow.start_run(run_name=args.run_name)
            mlflow.log_param("random_state", args.random_state)
            mlflow.log_param("result_file", args.result_csv_name)
            mlflow.log_param("balanced_authors_count", balanced_df['author'].nunique())

if __name__ == "__main__":
    main()
