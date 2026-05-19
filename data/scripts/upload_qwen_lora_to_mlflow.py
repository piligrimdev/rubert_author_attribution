import argparse
import mlflow
from mlflow.exceptions import RestException
from mlflow.tracking import MlflowClient


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--adapter-dir", required=True,
                   help="Local directory with lora adapter files")
    p.add_argument("--name", default="qwen_lora_stylizer")
    p.add_argument("--alias", default="stage")
    p.add_argument("--experiment", default="qwen_lora_stylizer")
    p.add_argument("--run-name", default="upload")
    p.add_argument("--base-model", default="Qwen/Qwen2.5-7B-Instruct")
    p.add_argument("--mlflow-tracking-uri", default="http://localhost:2000")
    args = p.parse_args()

    mlflow.set_tracking_uri(args.mlflow_tracking_uri)
    mlflow.set_experiment(args.experiment)
    client = MlflowClient()

    with mlflow.start_run(run_name=args.run_name) as run:
        mlflow.log_artifacts(args.adapter_dir, artifact_path="lora_adapter")
        source = mlflow.get_artifact_uri("lora_adapter")
        run_id = run.info.run_id

    try:
        client.create_registered_model(args.name)
    except RestException:
        pass

    mv = client.create_model_version(name=args.name, source=source, run_id=run_id)
    client.set_registered_model_alias(args.name, args.alias, mv.version)
    print(f"registered {args.name} v{mv.version} alias={args.alias} source={source}")


if __name__ == "__main__":
    main()
