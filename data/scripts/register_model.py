import argparse
import mlflow
import mlflow.pytorch
import torch
from shared.siamese_bert import SiameseBERT



def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mlflow-tracking-uri", default="http://localhost:2000")
    p.add_argument("--link-run-id", required=True)

    p.add_argument("--model-path", required=True)
    p.add_argument(
        "--model-name",
        default="rubert-author-attribution",
    )
    p.add_argument("--run-name", default="model_registration")
    p.add_argument(
        "--bert-base-name",
        default="DeepPavlov/rubert-base-cased",
    )
    args = p.parse_args()

    mlflow.set_tracking_uri(args.mlflow_tracking_uri)

    model = SiameseBERT(model_name=args.bert_base_name)
    state_dict = torch.load(args.model_path, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()

    with mlflow.start_run(run_id=args.link_run_id):

        model_info = mlflow.pytorch.log_model(
            pytorch_model=model,
            registered_model_name=args.model_name,
        )

        print(f"\nМодель зарегистрирована:")
        print(f"  URI:      {model_info.model_uri}")


if __name__ == "__main__":
    main()
