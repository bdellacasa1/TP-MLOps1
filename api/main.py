from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    HTTPException,
)

from api.model_service import model_service
from api.schemas import (
    PredictionRequest,
    PredictionResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    print(
        "Iniciando API..."
    )

    model_service.reload_model()

    yield

    print(
        "Deteniendo API..."
    )


app = FastAPI(
    title="Airline Satisfaction API",
    description=(
        "API de predicción de satisfacción "
        "de pasajeros."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():

    return {
        "message": (
            "Airline Satisfaction API"
        )
    }


@app.get("/health")
def health():

    return model_service.health()


@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(
    request: PredictionRequest,
):

    try:

        features = request.model_dump(
            by_alias=True
        )

        return model_service.predict(
            features
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@app.post("/reload-model")
def reload_model():
    """
    Recarga el modelo que actualmente tenga
    el alias champion.

    Airflow podrá llamar este endpoint
    después de un reentrenamiento exitoso.
    """

    try:

        return model_service.reload_model()

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc