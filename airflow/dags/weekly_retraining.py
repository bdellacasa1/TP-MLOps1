import pendulum

from airflow.sdk import dag, task
from airflow.providers.standard.operators.bash import BashOperator


MODEL_NAME = "airline_satisfaction_without_scores"
MLFLOW_URI = "http://mlflow:5000"
API_URL = "http://api:8000"


@dag(
    dag_id="weekly_airline_retraining",
    description=(
        "Reentrenamiento semanal del modelo de satisfacción "
        "de pasajeros y actualización de la API."
    ),
    schedule="59 23 * * 0",
    start_date=pendulum.datetime(
        2026,
        8,
        16,
        tz="America/Argentina/Buenos_Aires",
    ),
    catchup=False,
    max_active_runs=1,
    tags=["mlops", "airline", "retraining"],
)
def weekly_airline_retraining():

    # ---------------------------------------------------------
    # 1. Ejecutar pipeline completo de entrenamiento
    # ---------------------------------------------------------

    run_training_pipeline = BashOperator(
        task_id="run_training_pipeline",
        bash_command="python -m src.pipeline",
        cwd="/workspace",
        env={
            "MLFLOW_TRACKING_URI": MLFLOW_URI,
            "PYTHONPATH": "/workspace",
        },
        append_env=True,
    )

    # ---------------------------------------------------------
    # 2. Validar que exista un champion
    # ---------------------------------------------------------

    @task(task_id="validate_champion")
    def validate_champion():

        import mlflow
        from mlflow import MlflowClient

        mlflow.set_tracking_uri(
            MLFLOW_URI
        )

        client = MlflowClient()

        champion = (
            client.get_model_version_by_alias(
                MODEL_NAME,
                "champion",
            )
        )

        print(
            f"Champion encontrado: "
            f"version={champion.version}"
        )

        print(
            f"Run ID: {champion.run_id}"
        )

        return {
            "version": str(
                champion.version
            ),
            "run_id": champion.run_id,
        }

    champion = validate_champion()

    # ---------------------------------------------------------
    # 3. Recargar el champion en FastAPI
    # ---------------------------------------------------------

    reload_api_model = BashOperator(
        task_id="reload_api_model",
        bash_command=(
            f"curl -fsS "
            f"-X POST "
            f"{API_URL}/reload-model"
        ),
    )

    # ---------------------------------------------------------
    # 4. Validar que la API siga saludable
    # ---------------------------------------------------------

    validate_api = BashOperator(
        task_id="validate_api",
        bash_command=(
            f"curl -fsS "
            f"{API_URL}/health"
        ),
    )

    # ---------------------------------------------------------
    # Dependencias
    # ---------------------------------------------------------

    (
        run_training_pipeline
        >> champion
        >> reload_api_model
        >> validate_api
    )


weekly_airline_retraining()