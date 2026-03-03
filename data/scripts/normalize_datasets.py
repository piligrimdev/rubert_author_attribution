import argparse
import pandas as pd
from tqdm import tqdm

from shared.normailze_text import normalize_text
from shared.send_df_meta_to_mlflow import send_mlflow_df_metadata

def main():

    p = argparse.ArgumentParser()
    p.add_argument("--result_csv_name", default="concated_normalized.csv")

    p.add_argument("--dataset_path_ruslit", default="concated_full.csv")

    p.add_argument("--mlflow-tracking-uri", default="http://localhost:2000")
    p.add_argument("--run_name", default='normalization_full_dataset')
    p.add_argument("--use_mlflow", action="store_true")
    args = p.parse_args()

    dataset = pd.read_csv(args.dataset_path_ruslit)

    tqdm.pandas()
    dataset['text'] = dataset['text'].progress_apply(lambda x: normalize_text(x))

    dataset.to_csv(args.result_csv_name, index=False)

    if args.use_mlflow:
        if not args.mlflow_tracking_uri:
            raise RuntimeError("You need to specify mlflow tracking uri")
        send_mlflow_df_metadata(
            args.mlflow_tracking_uri,
            'normalization',
            args.run_name,
            dataset,
            '',
            args.result_csv_name,
        )

if __name__ == "__main__":
    main()
