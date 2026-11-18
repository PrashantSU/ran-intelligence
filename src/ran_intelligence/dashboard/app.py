"""RAN Intelligence Platform — Streamlit application."""

from datetime import UTC, date, datetime, time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from ran_intelligence.dashboard.client import api_request

st.set_page_config(
    page_title="RAN Intelligence Platform",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.8rem; padding-bottom: 2.5rem;}
    [data-testid="stMetric"] {
        background: rgba(128,128,128,0.07);
        border: 1px solid rgba(128,128,128,0.18);
        padding: 14px 16px;
        border-radius: 10px;
    }
    .small-note {font-size: 0.88rem; opacity: 0.78;}
    </style>
    """,
    unsafe_allow_html=True,
)


def api_get(path):
    return api_request("GET", path)


def api_post(path, payload):
    return api_request("POST", path, payload)


def show_error(exc):
    st.error(str(exc))


def as_frame(value):
    if isinstance(value, list):
        return pd.DataFrame(value)
    if isinstance(value, dict):
        return pd.DataFrame(value.get("data", []))
    return pd.DataFrame()


def metric_options(items):
    """Return {display label: API column name} from KPI metadata."""
    options = {}
    for item in items or []:
        if not isinstance(item, dict):
            continue
        column = item.get("column") or item.get("name")
        if not column:
            continue
        label = item.get("label") or item.get("display_name") or column
        unit = item.get("unit")
        if unit:
            label = f"{label} ({unit})"
        options[label] = column
    return options


def display_records(records, height=350):
    frame = as_frame(records)
    if frame.empty:
        st.info("No records to display.")
    else:
        st.dataframe(frame, use_container_width=True, height=height)
    return frame


def page_header(title, description):
    st.title(title)
    st.caption(description)


def load_context():
    """Fetch the lightweight data and KPI metadata used across pages."""
    data = api_get("/api/v1/data/summary")
    kpis = api_get("/api/v1/kpis")
    sessions = data.get("sessions", [])
    options = metric_options(kpis)
    return data, kpis, sessions, options


def overview():
    page_header(
        "RAN Intelligence Platform",
        "AI-powered 5G Radio Access Network analytics and incident investigation",
    )

    try:
        health = api_get("/health")
        data, kpis, sessions, _ = load_context()
    except Exception as exc:
        show_error(exc)
        st.info(
            "Start the FastAPI backend to load live network data. "
            "The dashboard is connected to the configured API URL."
        )
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("API status", health.get("status", "unknown").upper())
    c2.metric("Measurements", f'{data.get("rows", 0):,}')
    c3.metric("Sessions", len(sessions))
    c4.metric("Available KPIs", len(kpis))

    st.divider()
    left, right = st.columns([1.15, 1])

    with left:
        st.subheader("Dataset")
        st.write("**Sessions:**", ", ".join(sessions))
        st.write("**Columns:**", data.get("columns", "—"))
        st.write("**Environment:**", health.get("environment", "—"))
        st.write("**Application:**", health.get("app_name", "—"))

        st.subheader("Data quality")
        missing = data.get("missing_values", {})
        if missing:
            missing_frame = pd.DataFrame(
                [{"Metric": k, "Missing values": v}
                 for k, v in missing.items()]
            ).sort_values("Missing values", ascending=False)
            st.dataframe(missing_frame, use_container_width=True)
        else:
            st.success("No missing values reported.")

    with right:
        st.subheader("Session overview")
        try:
            sessions_data = api_get("/api/v1/kpis/sessions")
            display_records(sessions_data)
        except Exception as exc:
            show_error(exc)

    st.divider()
    st.subheader("Platform capabilities")
    cols = st.columns(4)
    capabilities = [
        ("📊", "KPI analytics", "Network measurement exploration"),
        ("🚨", "Anomaly detection", "Statistical anomaly signals"),
        ("📈", "Forecasting", "Chronological KPI evaluation"),
        ("📚", "Telecom RAG", "Hybrid standards-document retrieval"),
        ("🤖", "Incident agent", "Evidence-gathering workflow"),
        ("🧪", "Network simulation", "Simplified what-if analysis"),
        ("🧑‍⚖️", "Human review", "Explicit approval or rejection"),
        ("🔎", "Observability", "Evaluation and investigation traces"),
    ]
    for i, (icon, name, description) in enumerate(capabilities):
        with cols[i % 4]:
            st.markdown(f"**{icon} {name}**")
            st.caption(description)


def kpi_explorer(context):
    page_header(
        "KPI Explorer",
        "Explore measured radio indicators by session and aggregation interval.",
    )
    _, _, sessions, options = context

    if not sessions or not options:
        st.warning("No sessions or KPI definitions are available.")
        return

    with st.form("kpi_form"):
        c1, c2 = st.columns(2)
        session = c1.selectbox("Measurement session", sessions)
        label = c2.selectbox("KPI", list(options))
        c3, c4 = st.columns(2)
        interval = c3.selectbox(
            "Aggregation interval",
            ["1s", "5s", "10s", "30s", "1min"],
            index=4,
        )
        aggregation = c4.selectbox(
            "Aggregation",
            ["median", "mean", "min", "max"],
        )
        submitted = st.form_submit_button(
            "Load time series",
            type="primary",
        )

    if submitted:
        try:
            result = api_post(
                "/api/v1/kpis/timeseries",
                {
                    "session_id": session,
                    "metric": options[label],
                    "interval": interval,
                    "aggregation": aggregation,
                },
            )
            frame = as_frame(result)
            st.metric("Returned observations", result.get("count", len(frame)))

            if not frame.empty:
                time_col = next(
                    (c for c in ["timestamp", "time", "datetime"]
                     if c in frame.columns),
                    None,
                )
                value_col = options[label]
                if time_col and value_col in frame.columns:
                    frame[time_col] = pd.to_datetime(frame[time_col])
                    fig = px.line(
                        frame,
                        x=time_col,
                        y=value_col,
                        title=f"{label} — {session}",
                        markers=True,
                    )
                    fig.update_layout(
                        xaxis_title="Time",
                        yaxis_title=label,
                        hovermode="x unified",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Time-series response received; displaying its records.")
                display_records(frame)
            else:
                st.info("No observations returned for this selection.")
        except Exception as exc:
            show_error(exc)


def anomaly_detection(context):
    page_header(
        "Anomaly Detection",
        "Identify unusual KPI observations and contiguous anomaly episodes.",
    )
    _, _, _, options = context
    if not options:
        st.warning("No KPI definitions are available.")
        return

    with st.form("anomaly_form"):
        selected_labels = st.multiselect(
            "KPIs to analyse",
            list(options),
            default=list(options)[:2],
        )
        c1, c2, c3 = st.columns(3)
        threshold = c1.slider("Robust z-score threshold", 1.0, 6.0, 3.5, 0.1)
        min_samples = c2.number_input(
            "Minimum samples", min_value=5, max_value=1000, value=20
        )
        max_gap = c3.number_input(
            "Maximum episode gap (seconds)",
            min_value=0.0,
            max_value=60.0,
            value=2.0,
        )
        submitted = st.form_submit_button(
            "Detect anomalies",
            type="primary",
        )

    if submitted:
        if not selected_labels:
            st.warning("Select at least one KPI.")
            return
        try:
            result = api_post(
                "/api/v1/anomalies/detect",
                {
                    "metrics": [options[x] for x in selected_labels],
                    "threshold": threshold,
                    "min_samples": int(min_samples),
                    "max_gap_seconds": float(max_gap),
                    "limit": 100,
                },
            )
            a, b, c = st.columns(3)
            a.metric("Analysed observations", f'{result.get("analysed_observations", 0):,}')
            b.metric("Flagged observations", f'{result.get("flagged_observations", 0):,}')
            c.metric("Anomaly episodes", result.get("event_count", 0))

            st.info(result.get("interpretation", "Anomaly signals require investigation."))
            st.subheader("Anomaly episodes")
            display_records(result.get("events", []))
            st.subheader("Flagged observations")
            display_records(result.get("observations", []))
            if result.get("truncated"):
                st.caption("The API limited the returned records.")
        except Exception as exc:
            show_error(exc)


def forecasting(context):
    page_header(
        "KPI Forecasting",
        "Evaluate forecasting models using a chronological holdout from one measurement session.",
    )
    _, _, sessions, options = context
    if not sessions or not options:
        st.warning("No sessions or KPI definitions are available.")
        return

    with st.form("forecast_form"):
        c1, c2 = st.columns(2)
        session = c1.selectbox("Session", sessions)
        label = c2.selectbox("KPI", list(options))
        c3, c4, c5 = st.columns(3)
        frequency = c3.selectbox("Frequency", ["1s", "2s", "5s"], index=0)
        horizon = c4.number_input(
            "Forecast horizon (steps)", 1, 60, 5
        )
        test_fraction = c5.slider(
            "Test fraction", 0.1, 0.4, 0.2, 0.05
        )
        submitted = st.form_submit_button(
            "Evaluate forecast models",
            type="primary",
        )

    if submitted:
        try:
            result = api_post(
                "/api/v1/forecasts/evaluate",
                {
                    "session_id": session,
                    "metric": options[label],
                    "frequency": frequency,
                    "horizon_steps": int(horizon),
                    "test_fraction": float(test_fraction),
                    "gap_steps": 5,
                    "n_estimators": 100,
                    "min_samples_leaf": 3,
                    "limit": 200,
                },
            )

            c1, c2, c3 = st.columns(3)
            c1.metric("Series observations", result.get("series_observations", 0))
            c2.metric("Training observations", result.get("train_observations", 0))
            c3.metric("Test observations", result.get("test_observations", 0))

            st.subheader("Model evaluation")
            metrics = as_frame(result.get("metrics", []))
            if not metrics.empty:
                st.dataframe(metrics, use_container_width=True)
            else:
                st.info("No model metrics returned.")

            st.subheader("Predictions")
            predictions = as_frame(result.get("predictions", []))
            if not predictions.empty:
                st.dataframe(predictions, use_container_width=True)
                time_col = next(
                    (c for c in ["timestamp", "time", "target_timestamp"]
                     if c in predictions.columns),
                    None,
                )
                numeric_cols = predictions.select_dtypes(include="number").columns.tolist()
                if time_col and numeric_cols:
                    plot_frame = predictions.copy()
                    plot_frame[time_col] = pd.to_datetime(plot_frame[time_col])
                    fig = px.line(
                        plot_frame,
                        x=time_col,
                        y=numeric_cols,
                        title=f"Forecast evaluation — {label}",
                    )
                    st.plotly_chart(fig, use_container_width=True)

            st.warning(result.get("evaluation_note", ""))
        except Exception as exc:
            show_error(exc)


def telecom_rag():
    page_header(
        "Telecom RAG",
        "Search the indexed ETSI and 3GPP technical documents using hybrid retrieval.",
    )
    st.caption(
        "This page displays retrieved evidence passages. "
        "It does not generate an LLM answer."
    )

    with st.form("rag_form"):
        query = st.text_area(
            "Search question",
            placeholder="How does the 5G NR physical downlink shared channel work?",
            height=90,
        )
        c1, c2 = st.columns(2)
        top_k = c1.slider("Results to return", 1, 10, 5)
        candidate_k = c2.slider("Candidate pool", 5, 100, 30)
        submitted = st.form_submit_button(
            "Search documents",
            type="primary",
        )

    if submitted:
        if len(query.strip()) < 3:
            st.warning("Enter a query containing at least three characters.")
            return
        try:
            result = api_post(
                "/api/v1/rag/search",
                {
                    "query": query.strip(),
                    "top_k": top_k,
                    "candidate_k": candidate_k,
                    "rrf_k": 60,
                },
            )
            c1, c2 = st.columns(2)
            c1.metric("Retrieved passages", result.get("result_count", 0))
            c2.metric("Indexed documents", result.get("index_document_count", 0))
            st.caption(f"Retrieval: {result.get('retrieval_method', '—')}")

            for item in result.get("results", []):
                title = item.get("title") or item.get("source") or "Retrieved passage"
                page = item.get("page")
                heading = f"#{item.get('rank', '?')} · {title}"
                if page is not None:
                    heading += f" · Page {page}"
                with st.expander(heading, expanded=item.get("rank") == 1):
                    st.write(item.get("text", ""))
                    st.caption(
                        f"Source: {item.get('source', '—')} | "
                        f"Chunk: {item.get('chunk_id', '—')} | "
                        f"RRF score: {item.get('rrf_score', 0):.5f}"
                    )
                    st.caption(
                        f"Vector rank: {item.get('vector_rank', '—')} · "
                        f"BM25 rank: {item.get('bm25_rank', '—')}"
                    )
        except Exception as exc:
            show_error(exc)


def incident_investigation(context):
    page_header(
        "Incident Investigation",
        "Submit an incident, inspect collected evidence, and review the advisory report.",
    )
    _, _, sessions, options = context

    st.subheader("Start an investigation")
    if not sessions:
        st.warning("No measurement sessions are available.")
        return

    with st.form("incident_form"):
        description = st.text_area(
            "Incident description",
            placeholder="Describe the observed service degradation or network issue.",
        )
        c1, c2 = st.columns(2)
        session = c1.selectbox("Measurement session", sessions)
        cell_id = c2.text_input(
            "Cell ID (optional)",
            placeholder="e.g. 1",
        )
        c3, c4 = st.columns(2)
        start_date = c3.date_input("Start date", value=date(2023, 9, 15))
        start_time = c4.time_input("Start time", value=time(11, 32))
        c5, c6 = st.columns(2)
        end_date = c5.date_input("End date", value=date(2023, 9, 15))
        end_time = c6.time_input("End time", value=time(11, 45))
        severity = st.selectbox(
            "Severity",
            ["low", "medium", "high", "critical"],
            index=1,
        )
        suspected_labels = st.multiselect(
            "Suspected KPIs",
            list(options),
            default=[
                label for label, column in options.items()
                if column in ["nr_sinr_db", "lte_sinr_db"]
            ][:2],
        )
        submitted = st.form_submit_button(
            "Start investigation",
            type="primary",
        )

    if submitted:
        if not description.strip():
            st.warning("Enter an incident description.")
            return
        start_dt = datetime.combine(start_date, start_time).replace(
            tzinfo=UTC
        )
        end_dt = datetime.combine(end_date, end_time).replace(
            tzinfo=UTC
        )
        if end_dt <= start_dt:
            st.error("The end time must be later than the start time.")
            return
        if not suspected_labels:
            st.warning("Select at least one suspected KPI.")
            return

        payload = {
            "description": description.strip(),
            "session_id": session,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "severity": severity,
            "suspected_kpis": [options[x] for x in suspected_labels],
        }
        if cell_id.strip():
            payload["cell_id"] = cell_id.strip()

        try:
            result = api_post("/api/v1/incidents", payload)
            st.session_state["ran_incident_thread"] = result["thread_id"]
            st.success("Investigation submitted.")
        except Exception as exc:
            show_error(exc)

    thread_id = st.session_state.get("ran_incident_thread")
    if not thread_id:
        return

    st.divider()
    st.subheader("Investigation status")
    st.code(thread_id)

    try:
        state = api_get(f"/api/v1/incidents/{thread_id}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Status", state.get("investigation_status", "—"))
        c2.metric("Current step", state.get("current_step", "—"))
        c3.metric("Human review pending", "Yes" if state.get("pending_review") else "No")

        st.write("**Completed tools:**", ", ".join(state.get("completed_tools", [])) or "None")
        if state.get("errors"):
            st.warning("Tool errors were reported.")
            display_records(state["errors"])

        report = state.get("report")
        if report:
            st.subheader("Investigation report")
            st.markdown("**Summary**")
            st.write(report.get("summary", "No summary available."))

            st.markdown("**Hypotheses**")
            hypotheses = report.get("hypotheses", [])
            if hypotheses:
                display_records(hypotheses)
            else:
                st.info("No hypotheses passed evidence-reference validation.")

            st.markdown("**Evidence collected**")
            display_records(report.get("evidence", []))

            st.markdown("**Limitations**")
            for limitation in report.get("limitations", []):
                st.write(f"- {limitation}")

            st.markdown("**Recommended actions**")
            for action in report.get("recommended_actions", []):
                st.write(f"- {action}")

        if state.get("pending_review"):
            st.divider()
            st.subheader("Human review")
            st.warning(
                "This report is advisory. Review the evidence and limitations "
                "before approving it."
            )
            feedback = st.text_area(
                "Reviewer feedback (optional)",
                key=f"feedback_{thread_id}",
            )
            left, right = st.columns(2)
            if left.button("Approve report", type="primary"):
                try:
                    updated = api_post(
                        f"/api/v1/incidents/{thread_id}/review",
                        {"approved": True, "feedback": feedback or None},
                    )
                    st.session_state["incident_review_result"] = updated
                    st.rerun()
                except Exception as exc:
                    show_error(exc)
            if right.button("Reject report"):
                try:
                    updated = api_post(
                        f"/api/v1/incidents/{thread_id}/review",
                        {"approved": False, "feedback": feedback or None},
                    )
                    st.session_state["incident_review_result"] = updated
                    st.rerun()
                except Exception as exc:
                    show_error(exc)
        else:
            decision = state.get("review_approved")
            if decision is not None:
                st.success(
                    "Report approved." if decision else "Report rejected."
                )
            elif state.get("investigation_status") != "running":
                st.info("No human review is currently pending.")

    except Exception as exc:
        show_error(exc)


def architecture():
    page_header(
        "System Architecture",
        "Application components and the engineering workflow.",
    )
    image_path = (
        Path(__file__).resolve().parents[3]
        / "docs" / "images" / "architecture.png"
    )
    if image_path.exists():
        st.image(str(image_path), use_container_width=True)
    else:
        st.info("Architecture image is not present in the repository.")

    st.subheader("Application layers")
    layers = [
        ("Data engineering", "AERPAW ingestion, validation, Parquet storage"),
        ("Analytics", "KPI summaries, anomaly detection, forecasting"),
        ("Knowledge retrieval", "FAISS, BM25, reciprocal-rank fusion, reranking"),
        ("Incident agent", "LangGraph workflow, evidence tools, human review"),
        ("Simulation", "Simplified network what-if and 5G NR lab"),
        ("Evaluation", "Retrieval metrics, report checks, tracing and tool latency"),
        ("API", "FastAPI services and validated request schemas"),
        ("Frontend", "Streamlit dashboard"),
    ]
    for title, description in layers:
        st.markdown(f"**{title}** — {description}")

    st.divider()
    st.subheader("Important limitations")
    st.write(
        "- The AERPAW data contains two short measurement sessions; "
        "forecast evaluation is not evidence of unseen-session generalisation."
    )
    st.write(
        "- Throughput is sparsely matched to radio observations and "
        "has substantial missingness."
    )
    st.write(
        "- Anomaly signals are not confirmed network faults. "
        "Incident hypotheses require supporting evidence and human review."
    )
    st.write(
        "- The network digital twin is a simplified educational model, "
        "not a commercial 3GPP-compliant simulator."
    )
    st.write(
        "- Incident checkpoints are held in API process memory and do not "
        "survive an API restart."
    )


def main():
    with st.sidebar:
        st.title("📡 RAN Intelligence")
        st.caption("5G Network Intelligence Platform")
        page = st.radio(
            "Navigation",
            [
                "Overview",
                "KPI Explorer",
                "Anomaly Detection",
                "Forecasting",
                "Telecom RAG",
                "Incident Investigation",
                "Architecture",
            ],
        )
        st.divider()
        st.caption("Backend")
        st.code(
            __import__("os").getenv(
                "RAN_API_BASE_URL",
                "http://127.0.0.1:8000",
            ),
            language=None,
        )

    if page == "Overview":
        overview()
        return

    if page == "Telecom RAG":
        telecom_rag()
        return

    if page == "Architecture":
        architecture()
        return

    try:
        context = load_context()
    except Exception as exc:
        show_error(exc)
        st.info("Start the FastAPI backend and try again.")
        return

    if page == "KPI Explorer":
        kpi_explorer(context)
    elif page == "Anomaly Detection":
        anomaly_detection(context)
    elif page == "Forecasting":
        forecasting(context)
    elif page == "Incident Investigation":
        incident_investigation(context)


if __name__ == "__main__":
    main()
