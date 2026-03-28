import mlflow
import pandas as pd
import argparse
from shared.clean_named_entities import clean_named_entities



def main():

    p = argparse.ArgumentParser()
    p.add_argument("--result_csv_name", default="balanced_lit_cleaned_NE.csv")
    p.add_argument("--path_to_corpus")

    p.add_argument("--use_mlflow", action="store_true")
    p.add_argument("--mlflow-tracking-uri", default="http://localhost:2000")
    p.add_argument("--text_field", default='text', type=str)
    p.add_argument("--run_name", default="balancing_authors")
    args = p.parse_args()

    df = pd.read_csv(args.path_to_corpus)

    df[args.text_field].apply(lambda x: clean_named_entities(x))

    df.to_csv(args.result_csv_name, index=False)

    if args.use_mlflow:
        if not args.mlflow_tracking_uri:
            raise RuntimeError("You need to specify mlflow tracking uri")

        mlflow.set_tracking_uri(args.mlflow_tracking_uri)
        if mlflow.active_run() is None:
            mlflow.set_experiment('cleaning_named_entities')
            mlflow.start_run(run_name=args.run_name)

if __name__ == "__main__":
    main()
