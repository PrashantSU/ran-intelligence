"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ran_intelligence.api.schemas import (
    AnomalyRequest,
    ErrorResponse,
    ForecastRequest,
    HealthResponse,
    IncidentReviewRequest,
    IncidentSubmissionRequest,
    KpiTimeseriesRequest,
    RAGSearchRequest,
)
from ran_intelligence.api.services import (
    DataService,
    IncidentService,
    RAGService,
)
from ran_intelligence.core.config import get_settings
from ran_intelligence.core.exceptions import RANIntelligenceError
from ran_intelligence.ml.anomaly_pipeline import run_anomaly_pipeline
from ran_intelligence.ml.forecasting import (
    build_supervised_dataset,
    chronological_split,
    evaluate_forecasters,
    prepare_forecasting_series,
)


def _records(frame: pd.DataFrame) -> list[dict]:
    """Convert a DataFrame into JSON-safe records."""
    clean = frame.astype(object).where(pd.notna(frame), None)
    records = clean.to_dict(orient="records")

    for record in records:
        for key, value in record.items():
            if hasattr(value, "isoformat"):
                record[key] = value.isoformat()

    return records


def get_data_service(request: Request) -> DataService:
    # Also support TestClient usage without an explicit lifespan context.
    if not hasattr(request.app.state, "services"):
        request.app.state.services = {}
    if not hasattr(request.app.state, "settings"):
        request.app.state.settings = get_settings()

    services = request.app.state.services
    if "data" not in services:
        settings = request.app.state.settings
        data_path = (
            settings.project_root
            / "data"
            / "processed"
            / "aerpaw"
            / "aerpaw_measurements.parquet"
        )
        services["data"] = DataService(data_path)
    return services["data"]


def get_incident_service(request: Request) -> IncidentService:
    """Return the lazily initialized incident investigation service."""
    if not hasattr(request.app.state, "services"):
        request.app.state.services = {}

    services = request.app.state.services

    if "incident" not in services:
        measurements = get_data_service(request).measurements
        rag_service = get_rag_service(request)

        from ran_intelligence.agents.rag_tool import create_rag_handler

        def search_incident_documents(
            index,
            query: str,
            top_k: int = 5,
            candidate_k: int = 30,
        ):
            # RAGService loads its index and embedding model only on first use.
            response = rag_service.search(
                query=query,
                top_k=top_k,
                candidate_k=candidate_k,
            )

            return [
                {
                    "chunk_id": item["chunk_id"],
                    "text": item["text"],
                    "metadata": {
                        "source": item.get("source"),
                        "title": item.get("title"),
                        "page": item.get("page"),
                    },
                    "rrf_score": item.get("rrf_score", 0.0),
                }
                for item in response["results"]
            ]

        rag_handler = create_rag_handler(
            index={},
            search_fn=search_incident_documents,
        )

        services["incident"] = IncidentService(
            measurements,
            rag_handler=rag_handler,
        )

    return services["incident"]


def get_rag_service(request: Request) -> RAGService:
    """Return the lazily initialized RAG service."""
    if not hasattr(request.app.state, "services"):
        request.app.state.services = {}
    if not hasattr(request.app.state, "settings"):
        request.app.state.settings = get_settings()

    services = request.app.state.services

    if "rag" not in services:
        import os

        settings = request.app.state.settings
        index_path = Path(
            os.getenv(
                "RAN_RAG_INDEX_PATH",
                str(
                    settings.project_root
                    / "data"
                    / "processed"
                    / "etsi"
                    / "index"
                ),
            )
        )
        services["rag"] = RAGService(index_path)

    return services["rag"]


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    application.state.settings = get_settings()
    application.state.started_at = datetime.now(UTC)
    application.state.services = {}
    yield
    application.state.services.clear()


def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        description="API for RAN data analytics and incident intelligence.",
        version="0.1.0",
        lifespan=lifespan,
    )

    @application.get("/health", response_model=HealthResponse, tags=["System"])
    def health():
        return HealthResponse(
            status="ok",
            app_name=settings.app_name,
            environment=settings.app_env,
        )

    @application.get("/api/v1/data/summary", tags=["Data"])
    def data_summary(request: Request):
        try:
            return get_data_service(request).dataset_summary()
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @application.get("/api/v1/kpis", tags=["KPI Analytics"])
    def available_kpis(request: Request):
        return get_data_service(request).available_kpis()

    @application.get("/api/v1/kpis/summary", tags=["KPI Analytics"])
    def kpi_summary(request: Request):
        try:
            return _records(get_data_service(request).kpi_summary())
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @application.get("/api/v1/kpis/sessions", tags=["KPI Analytics"])
    def session_summary(request: Request):
        try:
            return _records(get_data_service(request).session_summary())
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @application.post("/api/v1/kpis/timeseries", tags=["KPI Analytics"])
    def kpi_timeseries(payload: KpiTimeseriesRequest, request: Request):
        try:
            frame = get_data_service(request).kpi_timeseries(
                session_id=payload.session_id,
                metric=payload.metric,
                interval=payload.interval,
                aggregation=payload.aggregation,
            )
            return {
                "session_id": payload.session_id,
                "metric": payload.metric,
                "interval": payload.interval,
                "aggregation": payload.aggregation,
                "count": len(frame),
                "data": _records(frame),
            }
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc


    @application.post("/api/v1/anomalies/detect", tags=["Anomaly Detection"])
    def detect_anomalies(payload: AnomalyRequest, request: Request):
        service = get_data_service(request)
        df = service.measurements

        if payload.metrics:
            available = {
                item["column"] for item in service.available_kpis()
            }
            invalid = sorted(set(payload.metrics) - available)
            if invalid:
                raise HTTPException(
                    status_code=422,
                    detail=f"Unknown KPI metrics: {invalid}",
                )

        output_dir = (
            request.app.state.settings.project_root
            / "artifacts"
            / "api"
            / "anomalies"
            / str(uuid4())
        )

        try:
            result = run_anomaly_pipeline(
                df=df,
                output_dir=output_dir,
                metrics=payload.metrics,
                threshold=payload.threshold,
                min_samples=payload.min_samples,
                max_gap_seconds=payload.max_gap_seconds,
            )
        except (ValueError, KeyError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        observations = result["observations"]
        events = result["events"]
        flagged = observations.loc[observations["is_anomaly"]]

        return {
            "input_rows": result["input_rows"],
            "analysed_observations": result["analysed_observations"],
            "flagged_observations": result["flagged_observations"],
            "event_count": result["event_count"],
            "sessions": result["sessions"],
            "metrics": result["metrics"],
            "observations": _records(flagged.head(payload.limit)),
            "events": _records(events.head(payload.limit)),
            "returned_observations": min(len(flagged), payload.limit),
            "returned_events": min(len(events), payload.limit),
            "truncated": (
                len(flagged) > payload.limit or len(events) > payload.limit
            ),
            "interpretation": (
                "Statistical anomalies are investigation signals, "
                "not confirmed network faults."
            ),
        }

    @application.post("/api/v1/forecasts/evaluate", tags=["Forecasting"])
    def evaluate_forecast(payload: ForecastRequest, request: Request):
        service = get_data_service(request)
        df = service.measurements

        available_sessions = set(
            df["session_id"].dropna().astype(str)
        )
        if payload.session_id not in available_sessions:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown session_id: {payload.session_id}",
            )

        available_metrics = {
            item["column"] for item in service.available_kpis()
        }
        if payload.metric not in available_metrics:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown KPI metric: {payload.metric}",
            )

        try:
            series = prepare_forecasting_series(
                df,
                session_id=payload.session_id,
                metric=payload.metric,
                frequency=payload.frequency,
                max_forward_fill=payload.max_forward_fill,
            )

            dataset = build_supervised_dataset(
                series,
                horizon_steps=payload.horizon_steps,
            )

            train, test = chronological_split(
                dataset,
                test_fraction=payload.test_fraction,
                gap_steps=payload.gap_steps,
            )

            if train.empty or test.empty:
                raise ValueError(
                    "Insufficient observations after chronological split."
                )

            predictions, metrics = evaluate_forecasters(
                train,
                test,
                n_estimators=payload.n_estimators,
                min_samples_leaf=payload.min_samples_leaf,
                random_state=42,
            )

        except (ValueError, KeyError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        return {
            "session_id": payload.session_id,
            "metric": payload.metric,
            "frequency": payload.frequency,
            "horizon_steps": payload.horizon_steps,
            "horizon_duration": (
                f"{payload.horizon_steps} x {payload.frequency}"
            ),
            "series_observations": len(series),
            "supervised_observations": len(dataset),
            "train_observations": len(train),
            "test_observations": len(test),
            "metrics": _records(metrics),
            "predictions": _records(predictions.tail(payload.limit)),
            "returned_predictions": min(len(predictions), payload.limit),
            "truncated": len(predictions) > payload.limit,
            "evaluation_note": (
                "Chronological holdout evaluation on this session. "
                "It does not establish generalisation to unseen sessions."
            ),
        }



    @application.post("/api/v1/rag/search", tags=["Telecom RAG"])
    def rag_search(payload: RAGSearchRequest, request: Request):
        service = get_rag_service(request)

        try:
            return service.search(
                query=payload.query,
                top_k=payload.top_k,
                candidate_k=payload.candidate_k,
                rrf_k=payload.rrf_k,
            )
        except FileNotFoundError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except (ValueError, KeyError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"RAG search is unavailable: {type(exc).__name__}: {exc}",
            ) from exc


    @application.post(
        "/api/v1/incidents",
        tags=["Incident Investigation"],
    )
    def start_incident(
        payload: IncidentSubmissionRequest,
        request: Request,
    ):
        from ran_intelligence.agents.schemas import IncidentRequest

        try:
            service = get_incident_service(request)
            incident = IncidentRequest.model_validate(payload.model_dump())
            return service.start(incident)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Incident investigation failed: {type(exc).__name__}: {exc}",
            ) from exc

    @application.get(
        "/api/v1/incidents/{thread_id}",
        tags=["Incident Investigation"],
    )
    def get_incident(thread_id: str, request: Request):
        try:
            return get_incident_service(request).get(thread_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @application.post(
        "/api/v1/incidents/{thread_id}/review",
        tags=["Incident Investigation"],
    )
    def review_incident(
        thread_id: str,
        payload: IncidentReviewRequest,
        request: Request,
    ):
        try:
            return get_incident_service(request).review(
                thread_id=thread_id,
                approved=payload.approved,
                feedback=payload.feedback,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Incident review failed: {type(exc).__name__}: {exc}",
            ) from exc

    @application.exception_handler(RANIntelligenceError)
    async def ran_error_handler(request: Request, exc: RANIntelligenceError):
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error=type(exc).__name__,
                message=str(exc),
                details=getattr(exc, "details", {}) or {},
            ).model_dump(mode="json"),
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        details = [
            {key: value for key, value in error.items() if key != "ctx"}
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "error": "ValidationError",
                "message": "Request validation failed.",
                "details": details,
            },
        )

    return application


app = create_app() is it front end of my app
