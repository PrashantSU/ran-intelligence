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
    '''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --ran-bg: #10141c;
        --ran-sidebar: #0b0f16;
        --ran-card: #181f2b;
        --ran-card-hover: #202a38;
        --ran-border: #293445;
        --ran-text: #f1f5f9;
        --ran-muted: #94a3b8;
        --ran-blue: #38bdf8;
        --ran-indigo: #818cf8;
        --ran-green: #34d399;
        --ran-amber: #fbbf24;
        --ran-red: #fb7185;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: var(--ran-bg);
        color: var(--ran-text);
    }

    [data-testid="stHeader"] {
        background: rgba(16, 20, 28, 0.92);
        border-bottom: 1px solid var(--ran-border);
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1500px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: var(--ran-sidebar);
        border-right: 1px solid var(--ran-border);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--ran-muted);
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 8px;
        padding: 5px 8px;
        transition: background 0.15s ease;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: var(--ran-card-hover);
    }

    h1, h2, h3 {
        color: var(--ran-text) !important;
        letter-spacing: -0.035em;
        font-weight: 700 !important;
    }

    h1 {
        font-size: 2rem !important;
        line-height: 1.25 !important;
    }

    h2 {
        font-size: 1.35rem !important;
    }

    h3 {
        font-size: 1.05rem !important;
    }

    p, li, label {
        color: #cbd5e1;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--ran-muted);
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #1b2533, #151c27);
        border: 1px solid var(--ran-border);
        border-radius: 12px;
        padding: 19px 20px;
        min-height: 112px;
        box-shadow: 0 5px 18px rgba(0, 0, 0, 0.12);
        transition: border-color 0.2s ease, transform 0.2s ease;
    }

    [data-testid="stMetric"]:hover {
        border-color: #3b82a8;
        transform: translateY(-2px);
    }

    [data-testid="stMetricLabel"] {
        color: var(--ran-muted) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--ran-text) !important;
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.04em;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.78rem !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--ran-card);
        border: 1px solid var(--ran-border);
        border-radius: 12px;
    }

    [data-testid="stForm"] {
        background: var(--ran-card);
        border: 1px solid var(--ran-border);
        border-radius: 12px;
        padding: 20px;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 8px;
        min-height: 42px;
        font-weight: 600;
        border: 1px solid var(--ran-border);
        transition: all 0.18s ease;
    }

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {
        background: #0284c7;
        border-color: #0284c7;
        color: white;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        border-color: var(--ran-blue);
        color: white;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input {
        background: #111925;
        border: 1px solid var(--ran-border);
        border-radius: 8px;
        color: var(--ran-text);
    }

    [data-testid="stSelectbox"] > div > div,
    [data-testid="stMultiSelect"] > div > div {
        background: #111925;
        border-color: var(--ran-border);
        border-radius: 8px;
    }

    [data-testid="stExpander"] {
        background: var(--ran-card);
        border: 1px solid var(--ran-border);
        border-radius: 10px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--ran-border);
        border-radius: 10px;
        overflow: hidden;
    }

    hr {
        border-color: var(--ran-border);
        margin: 1.5rem 0;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .small-note {
        color: var(--ran-muted);
        font-size: 0.84rem;
    }

    @media (max-width: 768px) {
        [data-testid="stMainBlockContainer"] {
            padding: 1.2rem 1rem 2rem;
        }
        h1 {
            font-size: 1.6rem !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.45rem !important;
        }
    }
    </style>
    ''',
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
    """Enterprise-style platform overview."""
    try:
        health = api_get("/health")
        data, kpis, sessions, _ = load_context()
    except Exception as exc:
        st.error(f"Unable to load platform data: {exc}")
        st.info("Check the FastAPI backend and refresh this page.")
        return

    st.markdown(
        """
        <div style="background:linear-gradient(115deg,#172638,#18243a);
        border:1px solid #30445a;border-radius:15px;padding:25px 28px;
        margin-bottom:22px;">
            <div style="color:#38bdf8;font-size:11px;font-weight:700;
            letter-spacing:2px;margin-bottom:9px;">
                NETWORK INTELLIGENCE · 5G RAN
            </div>
            <div style="color:#f1f5f9;font-size:27px;font-weight:750;
            letter-spacing:-1px;margin-bottom:7px;">
                RAN Intelligence Platform
            </div>
            <div style="color:#a9bacb;font-size:14px;">
                Network analytics, anomaly signals and AI-assisted
                incident investigation
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    status = str(health.get("status", "unknown")).upper()
    st.caption(
        f"● API {status}  |  Environment: "
        f"{health.get('environment', 'unknown')}  |  "
        f"{health.get('app_name', 'RAN Intelligence Platform')}"
    )

    st.markdown("### Platform at a glance")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Measurements", f'{data.get("rows", 0):,}')
    c2.metric("Measurement sessions", len(sessions))
    c3.metric("Available KPIs", len(kpis))
    c4.metric("Dataset columns", data.get("columns", "—"))

    st.divider()

    left, right = st.columns([1, 1.15], gap="large")

    with left:
        with st.container(border=True):
            st.markdown("### Dataset information")
            st.caption("Loaded measurement data")
            st.markdown("**Measurement sessions**")
            st.write(" · ".join(str(x) for x in sessions) or "None")
            st.markdown("**Data source**")
            st.write("AERPAW 5G measurement dataset")
            st.markdown("**Runtime environment**")
            st.write(health.get("environment", "—"))
            st.markdown("**Application**")
            st.write(health.get("app_name", "—"))

    with right:
        with st.container(border=True):
            st.markdown("### Measurement sessions")
            st.caption("Available sessions in the loaded dataset")
            try:
                sessions_data = api_get("/api/v1/kpis/sessions")
                session_frame = as_frame(sessions_data)
                if not session_frame.empty:
                    st.dataframe(
                        session_frame,
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("Session details are not available.")
            except Exception as exc:
                st.warning(f"Could not load session details: {exc}")

    st.divider()
    st.markdown("### Data quality")
    st.caption("Missing-value information reported by the backend")

    missing = data.get("missing_values", {}) or {}
    missing_frame = pd.DataFrame([
        {"Metric": str(key), "Missing values": int(value)}
        for key, value in missing.items()
    ])

    if not missing_frame.empty:
        missing_frame = missing_frame.sort_values(
            "Missing values", ascending=False
        )
        total_missing = int(missing_frame["Missing values"].sum())
        q1, q2 = st.columns([1, 2])

        with q1:
            st.metric("Reported missing values", f"{total_missing:,}")
            st.caption("Across reported dataset columns")

        with q2:
            nonzero = missing_frame[
                missing_frame["Missing values"] > 0
            ].head(12)

            if not nonzero.empty:
                fig = px.bar(
                    nonzero.sort_values("Missing values"),
                    x="Missing values",
                    y="Metric",
                    orientation="h",
                    template="plotly_dark",
                    color="Missing values",
                    color_continuous_scale=["#38bdf8", "#818cf8"],
                )
                fig.update_layout(
                    height=310,
                    margin=dict(l=10, r=10, t=15, b=10),
                    showlegend=False,
                    coloraxis_showscale=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis_title="Missing observations",
                    yaxis_title="",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("No missing values reported.")

        with st.expander("View complete data-quality report"):
            st.dataframe(
                missing_frame,
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("No per-column missing-value information was returned.")

    st.divider()
    st.markdown("### Intelligence capabilities")
    st.caption("Tools available across the platform")

    capabilities = [
        ("◈", "KPI analytics", "Explore radio measurements and time series."),
        ("⌁", "Anomaly detection", "Identify unusual KPI observations."),
        ("↗", "Forecasting", "Evaluate models using chronological holdouts."),
        ("⌕", "Telecom knowledge", "Search indexed ETSI and 3GPP documents."),
        ("◎", "Incident investigation", "Collect evidence with an AI-assisted workflow."),
        ("◇", "Human review", "Review advisory reports."),
        ("△", "Network simulation", "Explore simplified network scenarios."),
        ("⌘", "Observability", "Inspect evaluation and investigation traces."),
    ]

    cols = st.columns(4, gap="medium")
    for index, (symbol, title, description) in enumerate(capabilities):
        with cols[index % 4]:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="color:#38bdf8;font-size:23px;
                    margin-bottom:9px;">{symbol}</div>
                    <div style="color:#f1f5f9;font-size:14px;
                    font-weight:650;margin-bottom:6px;">{title}</div>
                    <div style="color:#94a3b8;font-size:12px;
                    line-height:1.55;">{description}</div>
                    """,
                    unsafe_allow_html=True,
                )

    st.divider()
    st.caption(
        "RAN Intelligence Platform · Decision-support and investigation only. "
        "Anomaly signals are not confirmed network faults."
    )


def kpi_explorer(context):
    """Explore radio KPIs with an enterprise-style analytics layout."""
    _, _, sessions, options = context

    st.markdown(
        "Explore radio performance measurements across sessions and "
        "aggregation intervals."
    )

    if not sessions or not options:
        st.warning("No sessions or KPI definitions are available.")
        return

    with st.container(border=True):
        st.markdown("#### Analysis configuration")
        st.caption("Choose the measurement data and aggregation settings.")

        with st.form("kpi_form"):
            c1, c2 = st.columns(2)
            session = c1.selectbox("Measurement session", sessions)
            label = c2.selectbox("Performance indicator", list(options))

            c3, c4 = st.columns(2)
            interval = c3.selectbox(
                "Aggregation interval",
                ["1s", "5s", "10s", "30s", "1min"],
                index=4,
            )
            aggregation = c4.selectbox(
                "Aggregation method",
                ["median", "mean", "min", "max"],
            )

            submitted = st.form_submit_button(
                "↗  Load time series",
                type="primary",
                use_container_width=True,
            )

    if submitted:
        try:
            with st.spinner("Loading KPI measurements..."):
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
            count = result.get("count", len(frame))

            st.markdown("### Analysis results")
            m1, m2, m3 = st.columns(3)
            m1.metric("Observations", f"{count:,}")
            m2.metric("Selected KPI", label)
            m3.metric("Aggregation", aggregation.title())

            if not frame.empty:
                time_col = next(
                    (
                        c for c in ["timestamp", "time", "datetime"]
                        if c in frame.columns
                    ),
                    None,
                )
                value_col = options[label]

                if time_col and value_col in frame.columns:
                    frame[time_col] = pd.to_datetime(
                        frame[time_col], errors="coerce"
                    )
                    frame[value_col] = pd.to_numeric(
                        frame[value_col], errors="coerce"
                    )
                    chart_frame = frame.dropna(
                        subset=[time_col, value_col]
                    ).sort_values(time_col)

                    if not chart_frame.empty:
                        with st.container(border=True):
                            st.markdown("#### KPI trend")
                            st.caption(
                                f"{label} · {session} · {interval} intervals"
                            )
                            fig = px.line(
                                chart_frame,
                                x=time_col,
                                y=value_col,
                                markers=False,
                                template="plotly_dark",
                            )
                            fig.update_traces(
                                line=dict(color="#38BDF8", width=2.5),
                                fill="tozeroy",
                                fillcolor="rgba(56,189,248,0.08)",
                            )
                            fig.update_layout(
                                height=390,
                                margin=dict(l=15, r=15, t=20, b=15),
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)",
                                hovermode="x unified",
                                xaxis_title="Measurement time",
                                yaxis_title=label,
                                font=dict(
                                    family="Inter, sans-serif",
                                    color="#94A3B8",
                                ),
                            )
                            fig.update_xaxes(showgrid=False, zeroline=False)
                            fig.update_yaxes(
                                gridcolor="rgba(148,163,184,0.12)",
                                zeroline=False,
                            )
                            st.plotly_chart(
                                fig, use_container_width=True
                            )
                    else:
                        st.info("No valid numeric observations to plot.")
                else:
                    st.info(
                        "Time-series data received, but the expected "
                        "timestamp or KPI column was not found."
                    )

                with st.expander("View measurement records"):
                    display_records(frame)
            else:
                st.info(
                    "No observations returned for this selection. "
                    "Try another session or aggregation interval."
                )

        except Exception as exc:
            show_error(exc)


def anomaly_detection(context):
    """Monitor KPI anomalies and inspect detected episodes."""
    _, _, _, options = context

    st.markdown(
        "Identify unusual radio KPI behaviour and investigate "
        "contiguous anomaly episodes."
    )

    if not options:
        st.warning("No KPI definitions are available.")
        return

    with st.container(border=True):
        st.markdown("#### Detection configuration")
        st.caption("Configure the indicators and sensitivity of the detector.")

        with st.form("anomaly_form"):
            selected_labels = st.multiselect(
                "Performance indicators",
                list(options),
                default=list(options)[:2],
            )

            c1, c2, c3 = st.columns(3)
            threshold = c1.slider(
                "Robust z-score threshold", 1.0, 6.0, 3.5, 0.1
            )
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
                "⌁  Run anomaly detection",
                type="primary",
                use_container_width=True,
            )

    if submitted:
        if not selected_labels:
            st.warning("Select at least one KPI.")
            return

        try:
            with st.spinner("Analysing KPI observations..."):
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

            analysed = result.get("analysed_observations", 0)
            flagged = result.get("flagged_observations", 0)
            episodes = result.get("event_count", 0)

            st.markdown("### Detection summary")
            a, b, c = st.columns(3)
            a.metric("Analysed observations", f"{analysed:,}")
            b.metric("Flagged observations", f"{flagged:,}")
            c.metric("Anomaly episodes", episodes)

            if flagged > 0:
                st.warning(
                    f"{flagged:,} observations were flagged for further "
                    "investigation. These are anomaly signals, not "
                    "confirmed network faults."
                )
            else:
                st.success(
                    "No observations were flagged using the selected "
                    "detection settings."
                )

            with st.container(border=True):
                st.markdown("#### Detector interpretation")
                st.write(
                    result.get(
                        "interpretation",
                        "Anomaly signals require investigation.",
                    )
                )
                st.caption(
                    f"Indicators: {', '.join(selected_labels)}  ·  "
                    f"Threshold: {threshold:.1f}  ·  "
                    f"Minimum samples: {int(min_samples)}"
                )

            st.markdown("### Investigation evidence")
            events = result.get("events", [])
            observations = result.get("observations", [])

            tab1, tab2 = st.tabs([
                f"Anomaly episodes ({episodes})",
                f"Flagged observations ({flagged})",
            ])

            with tab1:
                if events:
                    display_records(events)
                else:
                    st.info("No anomaly episodes were returned.")

            with tab2:
                if observations:
                    display_records(observations)
                else:
                    st.info("No flagged observations were returned.")

            if result.get("truncated"):
                st.caption(
                    "The API limited the returned records. "
                    "The displayed evidence may not include every detection."
                )

        except Exception as exc:
            show_error(exc)


def forecasting(context):
    """Evaluate KPI forecasting models with a clear results layout."""
    _, _, sessions, options = context

    st.markdown(
        "Evaluate forecasting models using a chronological holdout "
        "from a selected measurement session."
    )

    if not sessions or not options:
        st.warning("No sessions or KPI definitions are available.")
        return

    with st.container(border=True):
        st.markdown("#### Forecast configuration")
        st.caption("Choose the time series and evaluation settings.")

        with st.form("forecast_form"):
            c1, c2 = st.columns(2)
            session = c1.selectbox("Measurement session", sessions)
            label = c2.selectbox("Performance indicator", list(options))

            c3, c4, c5 = st.columns(3)
            frequency = c3.selectbox(
                "Sampling frequency", ["1s", "2s", "5s"], index=0
            )
            horizon = c4.number_input(
                "Forecast horizon (steps)", 1, 60, 5
            )
            test_fraction = c5.slider(
                "Test fraction", 0.1, 0.4, 0.2, 0.05
            )

            submitted = st.form_submit_button(
                "↗  Evaluate forecast models",
                type="primary",
                use_container_width=True,
            )

    if submitted:
        try:
            with st.spinner("Training and evaluating forecasting models..."):
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

            st.markdown("### Evaluation overview")
            c1, c2, c3 = st.columns(3)
            c1.metric(
                "Series observations",
                f'{result.get("series_observations", 0):,}',
            )
            c2.metric(
                "Training observations",
                f'{result.get("train_observations", 0):,}',
            )
            c3.metric(
                "Test observations",
                f'{result.get("test_observations", 0):,}',
            )

            metrics = as_frame(result.get("metrics", []))
            predictions = as_frame(result.get("predictions", []))

            st.markdown("### Model performance")
            if not metrics.empty:
                with st.container(border=True):
                    st.caption(
                        "Compare the returned evaluation metrics "
                        "across forecasting models."
                    )
                    st.dataframe(
                        metrics,
                        use_container_width=True,
                        hide_index=True,
                    )
            else:
                st.info("No model metrics were returned.")

            st.markdown("### Forecast results")
            if not predictions.empty:
                time_col = next(
                    (
                        col for col in [
                            "timestamp", "time", "target_timestamp"
                        ]
                        if col in predictions.columns
                    ),
                    None,
                )
                numeric_cols = predictions.select_dtypes(
                    include="number"
                ).columns.tolist()

                if time_col and numeric_cols:
                    plot_frame = predictions.copy()
                    plot_frame[time_col] = pd.to_datetime(
                        plot_frame[time_col], errors="coerce"
                    )
                    plot_frame = plot_frame.dropna(subset=[time_col])

                    with st.container(border=True):
                        st.markdown("#### Actual vs predicted values")
                        st.caption(
                            f"{label} · {session} · {frequency} frequency"
                        )

                        fig = px.line(
                            plot_frame,
                            x=time_col,
                            y=numeric_cols,
                            template="plotly_dark",
                        )
                        fig.update_layout(
                            height=390,
                            margin=dict(l=15, r=15, t=20, b=15),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            hovermode="x unified",
                            xaxis_title="Target time",
                            yaxis_title=label,
                            font=dict(
                                family="Inter, sans-serif",
                                color="#94A3B8",
                            ),
                        )
                        fig.update_xaxes(showgrid=False)
                        fig.update_yaxes(
                            gridcolor="rgba(148,163,184,0.12)"
                        )
                        st.plotly_chart(
                            fig, use_container_width=True
                        )
                else:
                    st.info(
                        "Predictions were returned, but no compatible "
                        "time or numeric columns were found for plotting."
                    )

                with st.expander("View prediction records"):
                    display_records(predictions)
            else:
                st.info("No prediction records were returned.")

            evaluation_note = result.get("evaluation_note", "")
            if evaluation_note:
                st.warning(evaluation_note)

        except Exception as exc:
            show_error(exc)



def telecom_rag():
    page_header(
        "Telecom Knowledge",
        "Search technical standards and specifications across the indexed 3GPP and ETSI document collection.",
    )

    st.markdown(
        """
        <div style="background:linear-gradient(115deg,#172B40,#182337 55%,#20213B);
                    border:1px solid #30445D;border-radius:14px;
                    padding:20px 22px;margin:8px 0 20px 0;">
            <div style="color:#7DD3FC;font-size:11px;font-weight:700;
                        letter-spacing:1.5px;margin-bottom:8px;">
                TECHNICAL KNOWLEDGE BASE
            </div>
            <div style="font-size:21px;font-weight:650;color:#F1F5F9;
                        margin-bottom:7px;">
                Find evidence across telecom standards
            </div>
            <div style="font-size:13px;color:#B7C5D6;line-height:1.6;">
                Hybrid semantic and keyword retrieval helps locate relevant
                passages in technical specifications. Review original
                source passages before drawing conclusions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Document search")
    st.caption(
        "Search returns retrieved evidence passages, not a generated LLM answer."
    )

    with st.container(border=True):
        with st.form("rag_form"):
            query = st.text_area(
                "What do you want to investigate?",
                placeholder=(
                    "Example: How does the 5G NR physical downlink "
                    "shared channel work?"
                ),
                height=105,
            )

            st.markdown("**Retrieval settings**")
            c1, c2 = st.columns(2)
            top_k = c1.slider("Passages to display", 1, 10, 5)
            candidate_k = c2.slider("Candidate pool size", 5, 100, 30)

            submitted = st.form_submit_button(
                "Search knowledge base",
                type="primary",
                use_container_width=True,
            )

    if submitted:
        if len(query.strip()) < 3:
            st.warning("Enter a search question containing at least three characters.")
            return

        try:
            with st.spinner("Searching technical document collection..."):
                result = api_post(
                    "/api/v1/rag/search",
                    {
                        "query": query.strip(),
                        "top_k": top_k,
                        "candidate_k": candidate_k,
                        "rrf_k": 60,
                    },
                )

            results = result.get("results", [])
            result_count = result.get("result_count", len(results))
            document_count = result.get("index_document_count", 0)
            retrieval_method = result.get("retrieval_method", "—")

            st.markdown("#### Search results")

            m1, m2, m3 = st.columns(3)
            m1.metric("Retrieved passages", result_count)
            m2.metric("Indexed documents", document_count)
            m3.metric("Display limit", top_k)

            st.caption(f"Retrieval method: **{retrieval_method}**")

            if not results:
                st.info(
                    "No passages were returned. Try a broader question or "
                    "increase the candidate pool size."
                )
                return

            st.markdown(
                f"**{len(results)} passages returned** · "
                "Ranked using hybrid retrieval"
            )

            for item in results:
                rank = item.get("rank", "?")
                title = (
                    item.get("title")
                    or item.get("source")
                    or "Retrieved passage"
                )
                page = item.get("page")
                source_name = item.get("source", "—")
                chunk_id = item.get("chunk_id", "—")

                try:
                    score = float(item.get("rrf_score", 0) or 0)
                    score_label = f"{score:.5f}"
                except (TypeError, ValueError):
                    score_label = str(item.get("rrf_score", "—"))

                heading = title
                if page is not None:
                    heading += f" · Page {page}"

                with st.container(border=True):
                    left, right = st.columns([5, 1])
                    left.markdown(f"**{rank}. {heading}**")
                    right.markdown(
                        f"<div style='text-align:right;color:#7DD3FC;"
                        f"font-size:12px;font-weight:650;'>"
                        f"RRF {score_label}</div>",
                        unsafe_allow_html=True,
                    )

                    if rank == 1:
                        st.caption("TOP RETRIEVAL RESULT")

                    st.markdown(
                        item.get("text", "") or "_No passage text returned._"
                    )

                    st.divider()

                    meta1, meta2, meta3 = st.columns(3)
                    meta1.caption(f"Source: {source_name}")
                    meta2.caption(f"Chunk: {chunk_id}")
                    meta3.caption(
                        f"Vector rank: {item.get('vector_rank', '—')} · "
                        f"BM25 rank: {item.get('bm25_rank', '—')}"
                    )

            st.caption(
                "Retrieval scores indicate ranking within this result set; "
                "they do not establish that a passage is authoritative for "
                "every interpretation."
            )

        except Exception as exc:
            show_error(exc)

def incident_investigation(context):
    page_header(
        "Incident Investigation",
        "AI-assisted network incident analysis with evidence-backed findings and human review.",
    )
    _, _, sessions, options = context

    st.markdown(
        """
        <div style="background:linear-gradient(115deg,#20283B,#192536 60%,#25213B);
                    border:1px solid #35445C;border-radius:14px;
                    padding:19px 22px;margin:8px 0 20px 0;">
            <div style="color:#7DD3FC;font-size:11px;font-weight:700;
                        letter-spacing:1.4px;margin-bottom:8px;">
                AI INCIDENT RESPONSE
            </div>
            <div style="font-size:21px;font-weight:650;color:#F1F5F9;
                        margin-bottom:7px;">
                Investigate. Review evidence. Make informed decisions.
            </div>
            <div style="font-size:13px;color:#B7C5D6;line-height:1.6;">
                The investigation agent collects network evidence and prepares
                advisory hypotheses. Human approval remains part of the workflow.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not sessions:
        st.warning("No measurement sessions are available.")
        return

    st.markdown("#### New investigation")

    with st.container(border=True):
        with st.form("incident_form"):
            description = st.text_area(
                "Incident description",
                placeholder=(
                    "Describe the observed service degradation, affected area, "
                    "or suspected network issue."
                ),
                height=100,
            )

            st.markdown("**Network context**")
            c1, c2 = st.columns(2)
            session = c1.selectbox("Measurement session", sessions)
            cell_id = c2.text_input(
                "Cell ID (optional)",
                placeholder="e.g. 1",
            )

            st.markdown("**Investigation time window (UTC)**")
            c1, c2 = st.columns(2)
            start_date = c1.date_input(
                "Start date",
                value=date(2023, 9, 15),
            )
            start_time = c2.time_input(
                "Start time",
                value=time(11, 32),
            )

            c1, c2 = st.columns(2)
            end_date = c1.date_input(
                "End date",
                value=date(2023, 9, 15),
            )
            end_time = c2.time_input(
                "End time",
                value=time(11, 45),
            )

            st.markdown("**Incident classification**")
            c1, c2 = st.columns(2)
            severity = c1.selectbox(
                "Severity",
                ["low", "medium", "high", "critical"],
                index=1,
            )
            suspected_labels = c2.multiselect(
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
                use_container_width=True,
            )

    if submitted:
        if not description.strip():
            st.warning("Enter an incident description.")
            return

        start_dt = datetime.combine(start_date, start_time).replace(tzinfo=UTC)
        end_dt = datetime.combine(end_date, end_time).replace(tzinfo=UTC)

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
            with st.spinner("Submitting incident to the investigation agent..."):
                result = api_post("/api/v1/incidents", payload)

            st.session_state["ran_incident_thread"] = result["thread_id"]
            st.success("Investigation submitted successfully.")

        except Exception as exc:
            show_error(exc)

    thread_id = st.session_state.get("ran_incident_thread")
    if not thread_id:
        st.info(
            "Submit an incident to begin an investigation. "
            "Its progress and report will appear here."
        )
        return

    st.divider()
    st.markdown("#### Investigation workspace")

    st.caption("Investigation thread")
    st.code(thread_id, language=None)

    try:
        with st.spinner("Loading investigation state..."):
            state = api_get(f"/api/v1/incidents/{thread_id}")

        status = state.get("investigation_status", "—")
        current_step = state.get("current_step", "—")
        pending_review = state.get("pending_review", False)

        c1, c2, c3 = st.columns(3)
        c1.metric("Investigation status", str(status).replace("_", " ").title())
        c2.metric("Current step", current_step)
        c3.metric("Human review", "Pending" if pending_review else "Not pending")

        if pending_review:
            st.warning("Human review required before this report can be approved.")
        elif status == "running":
            st.info("The investigation is still running.")
        elif status == "completed":
            st.success("Investigation processing completed.")

        completed_tools = state.get("completed_tools", [])
        with st.expander("Investigation execution details", expanded=False):
            st.markdown("**Completed tools**")
            st.write(", ".join(completed_tools) if completed_tools else "None")

            if state.get("errors"):
                st.warning("Tool errors were reported.")
                display_records(state["errors"])

        report = state.get("report")

        if report:
            st.divider()
            st.markdown("#### Investigation report")

            st.markdown(
                """
                <div style="color:#94A3B8;font-size:12px;margin-bottom:12px;">
                    ADVISORY ANALYSIS · REVIEW SOURCE EVIDENCE BEFORE ACTING
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("**Executive summary**")
            with st.container(border=True):
                st.write(report.get("summary", "No summary available."))

            hypotheses = report.get("hypotheses", [])
            evidence = report.get("evidence", [])
            limitations = report.get("limitations", [])
            actions = report.get("recommended_actions", [])

            st.markdown("**Investigation findings**")
            h1, h2 = st.columns(2)
            h1.metric("Hypotheses", len(hypotheses))
            h2.metric("Evidence items", len(evidence))

            if hypotheses:
                display_records(hypotheses)
            else:
                st.info(
                    "No hypotheses passed evidence-reference validation."
                )

            with st.expander("Collected evidence", expanded=True):
                if evidence:
                    display_records(evidence)
                else:
                    st.info("No evidence items were returned.")

            with st.expander("Limitations and uncertainty", expanded=True):
                if limitations:
                    for limitation in limitations:
                        st.markdown(f"- {limitation}")
                else:
                    st.info("No limitations were returned.")

            with st.expander("Recommended actions", expanded=True):
                if actions:
                    for action in actions:
                        st.markdown(f"- {action}")
                else:
                    st.info("No recommended actions were returned.")

        if pending_review:
            st.divider()
            st.markdown("#### Human review")

            st.warning(
                "This is an advisory report, not an automated network-control "
                "decision. Review the evidence and limitations before choosing "
                "whether to approve it."
            )

            feedback = st.text_area(
                "Reviewer feedback (optional)",
                key=f"feedback_{thread_id}",
                placeholder="Add comments, corrections, or reasons for rejection.",
            )

            left, right = st.columns(2)

            if left.button(
                "Approve report",
                type="primary",
                use_container_width=True,
            ):
                try:
                    updated = api_post(
                        f"/api/v1/incidents/{thread_id}/review",
                        {"approved": True, "feedback": feedback or None},
                    )
                    st.session_state["incident_review_result"] = updated
                    st.rerun()
                except Exception as exc:
                    show_error(exc)

            if right.button(
                "Reject report",
                use_container_width=True,
            ):
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
                if decision:
                    st.success("The investigation report was approved.")
                else:
                    st.error("The investigation report was rejected.")
            elif status != "running":
                st.info("No human review is currently pending.")

    except Exception as exc:
        show_error(exc)

def architecture():
    page_header(
        "System Architecture",
        "End-to-end architecture, component responsibilities, and engineering decisions.",
    )

    st.markdown(
        """
        <div style="background:linear-gradient(115deg,#172B40,#182337 60%,#20213B);
                    border:1px solid #30445D;border-radius:14px;
                    padding:20px 22px;margin:8px 0 20px 0;">
            <div style="color:#7DD3FC;font-size:11px;font-weight:700;
                        letter-spacing:1.5px;margin-bottom:8px;">
                PLATFORM BLUEPRINT
            </div>
            <div style="font-size:21px;font-weight:650;color:#F1F5F9;
                        margin-bottom:7px;">
                From raw network measurements to actionable intelligence
            </div>
            <div style="font-size:13px;color:#B7C5D6;line-height:1.6;">
                A modular architecture combining data engineering, network
                analytics, hybrid retrieval, agentic investigation, and
                human oversight.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Architecture overview")

    st.markdown(
        """
        <div style="background:#111925;border:1px solid #29384A;
                    border-radius:14px;padding:18px;margin-bottom:14px;">
            <div style="color:#7DD3FC;font-size:11px;font-weight:700;
                        letter-spacing:1.2px;margin-bottom:12px;">
                01 · DATA FOUNDATION
            </div>
            <div style="background:#1B2939;border:1px solid #38516A;
                        border-radius:10px;padding:15px;text-align:center;">
                <div style="font-size:17px;font-weight:650;color:#F1F5F9;">
                    AERPAW 5G measurements
                </div>
                <div style="font-size:12px;color:#A9B9CB;margin-top:5px;">
                    Radio KPIs · Throughput · Measurement sessions
                </div>
            </div>
            <div style="text-align:center;color:#38BDF8;font-size:22px;
                        padding:5px;">↓</div>
            <div style="background:#1B2939;border:1px solid #38516A;
                        border-radius:10px;padding:13px;text-align:center;">
                <div style="font-weight:650;color:#F1F5F9;">
                    Ingestion · Validation · Parquet storage
                </div>
                <div style="font-size:12px;color:#A9B9CB;margin-top:4px;">
                    Data quality checks and processing
                </div>
            </div>
        </div>

        <div style="text-align:center;color:#38BDF8;font-size:22px;">↓</div>

        <div style="background:#111925;border:1px solid #29384A;
                    border-radius:14px;padding:18px;margin:10px 0;">
            <div style="color:#7DD3FC;font-size:11px;font-weight:700;
                        letter-spacing:1.2px;margin-bottom:12px;">
                02 · INTELLIGENCE SERVICES
            </div>
            <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
                        gap:10px;">
                <div style="background:#1B2939;border:1px solid #38516A;
                            border-radius:10px;padding:14px;">
                    <div style="color:#38BDF8;font-size:12px;font-weight:700;">
                        ANALYTICS
                    </div>
                    <div style="color:#F1F5F9;font-weight:650;margin:7px 0;">
                        KPI Intelligence
                    </div>
                    <div style="color:#A9B9CB;font-size:12px;line-height:1.6;">
                        KPI exploration<br/>Anomaly detection<br/>Forecast evaluation
                    </div>
                </div>
                <div style="background:#1B2939;border:1px solid #38516A;
                            border-radius:10px;padding:14px;">
                    <div style="color:#A5B4FC;font-size:12px;font-weight:700;">
                        KNOWLEDGE RETRIEVAL
                    </div>
                    <div style="color:#F1F5F9;font-weight:650;margin:7px 0;">
                        Telecom RAG
                    </div>
                    <div style="color:#A9B9CB;font-size:12px;line-height:1.6;">
                        FAISS vector search<br/>BM25 keyword retrieval<br/>RRF fusion and reranking
                    </div>
                </div>
                <div style="background:#1B2939;border:1px solid #38516A;
                            border-radius:10px;padding:14px;">
                    <div style="color:#34D399;font-size:12px;font-weight:700;">
                        AGENT WORKFLOW
                    </div>
                    <div style="color:#F1F5F9;font-weight:650;margin:7px 0;">
                        Incident Investigation
                    </div>
                    <div style="color:#A9B9CB;font-size:12px;line-height:1.6;">
                        LangGraph orchestration<br/>Evidence collection<br/>Human review
                    </div>
                </div>
                <div style="background:#1B2939;border:1px solid #38516A;
                            border-radius:10px;padding:14px;">
                    <div style="color:#FBBF24;font-size:12px;font-weight:700;">
                        SIMULATION
                    </div>
                    <div style="color:#F1F5F9;font-weight:650;margin:7px 0;">
                        Network Digital Twin
                    </div>
                    <div style="color:#A9B9CB;font-size:12px;line-height:1.6;">
                        What-if analysis<br/>Simplified 5G NR lab<br/>Scenario exploration
                    </div>
                </div>
            </div>
        </div>

        <div style="text-align:center;color:#38BDF8;font-size:22px;">↓</div>

        <div style="background:#111925;border:1px solid #29384A;
                    border-radius:14px;padding:18px;margin:10px 0;">
            <div style="color:#7DD3FC;font-size:11px;font-weight:700;
                        letter-spacing:1.2px;margin-bottom:12px;">
                03 · SERVICE AND PRESENTATION
            </div>
            <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
                        gap:10px;">
                <div style="background:#1B2939;border:1px solid #38516A;
                            border-radius:10px;padding:15px;text-align:center;">
                    <div style="font-size:12px;color:#38BDF8;font-weight:700;">
                        SERVICE LAYER
                    </div>
                    <div style="font-size:17px;color:#F1F5F9;
                                font-weight:650;margin:7px 0;">
                        FastAPI
                    </div>
                    <div style="font-size:12px;color:#A9B9CB;">
                        REST endpoints · Request validation
                    </div>
                </div>
                <div style="background:#1B2939;border:1px solid #38516A;
                            border-radius:10px;padding:15px;text-align:center;">
                    <div style="font-size:12px;color:#A5B4FC;font-weight:700;">
                        USER INTERFACE
                    </div>
                    <div style="font-size:17px;color:#F1F5F9;
                                font-weight:650;margin:7px 0;">
                        Streamlit
                    </div>
                    <div style="font-size:12px;color:#A9B9CB;">
                        Interactive dashboard · Visual analytics
                    </div>
                </div>
            </div>
            <div style="text-align:center;color:#94A3B8;font-size:12px;
                        margin-top:12px;">
                API-backed application · Advisory decision support
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Engineering components")

    components = [
        (
            "Data engineering",
            "AERPAW ingestion, validation, transformation, and Parquet storage.",
            "Data foundation",
        ),
        (
            "KPI analytics",
            "Session-level KPI exploration, anomaly detection, and forecasting evaluation.",
            "Analytics",
        ),
        (
            "Hybrid retrieval",
            "FAISS vector search, BM25 keyword retrieval, reciprocal-rank fusion, and reranking.",
            "Knowledge",
        ),
        (
            "Incident agent",
            "LangGraph orchestration, evidence tools, report generation, and human review.",
            "Agentic AI",
        ),
        (
            "Digital twin",
            "Simplified network scenarios and a 5G NR educational simulation environment.",
            "Simulation",
        ),
        (
            "Evaluation and observability",
            "Retrieval evaluation, report checks, execution tracing, and tool latency.",
            "Quality",
        ),
        (
            "Backend API",
            "FastAPI services with validated request schemas and application endpoints.",
            "Backend",
        ),
        (
            "Frontend",
            "Streamlit interface for analytics, knowledge retrieval, and incident investigation.",
            "Frontend",
        ),
    ]

    for i in range(0, len(components), 2):
        left, right = st.columns(2)
        for col, component in zip((left, right), components[i:i + 2]):
            title, description, category = component
            with col:
                with st.container(border=True):
                    st.caption(category.upper())
                    st.markdown(f"**{title}**")
                    st.write(description)

    st.divider()
    st.markdown("#### Scope and engineering limitations")

    limitations = [
        (
            "Dataset coverage",
            "The AERPAW dataset contains two short measurement sessions. "
            "Forecast evaluation does not establish generalisation to unseen sessions.",
        ),
        (
            "Throughput completeness",
            "Throughput is sparsely matched to radio observations and has substantial missingness.",
        ),
        (
            "Anomaly interpretation",
            "Anomaly signals are not confirmed network faults. Incident hypotheses require "
            "supporting evidence and human review.",
        ),
        (
            "Simulation fidelity",
            "The digital twin is a simplified model, not a commercial 3GPP-compliant link-level simulator.",
        ),
        (
            "Agent persistence",
            "Incident checkpoints are held in API process memory and do not survive an API restart.",
        ),
    ]

    for title, description in limitations:
        with st.expander(title):
            st.write(description)

    st.caption(
        "The platform provides advisory intelligence and does not directly control live network infrastructure."
    )
def main():
    """Enterprise-style application shell and navigation."""

    pages = {
        "Overview": ("⌂", "Platform overview"),
        "KPI Explorer": ("◈", "Explore network measurements"),
        "Anomaly Detection": ("⌁", "Detect unusual KPI behaviour"),
        "Forecasting": ("↗", "Evaluate KPI forecasts"),
        "Telecom Knowledge": ("⌕", "Search telecom documentation"),
        "Incident Investigation": ("◎", "Investigate network incidents"),
        "Architecture": ("◇", "Platform architecture"),
    }

    with st.sidebar:
        st.markdown(
            """
            <div style="padding:9px 2px 19px 2px;">
                <div style="display:flex;align-items:center;gap:11px;">
                    <div style="background:#123047;border:1px solid #24516d;
                    border-radius:11px;width:42px;height:42px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:22px;color:#38bdf8;">◉</div>
                    <div>
                        <div style="font-size:15px;font-weight:750;
                        color:#f1f5f9;">RAN Intelligence</div>
                        <div style="font-size:10px;color:#94a3b8;
                        letter-spacing:1.2px;">NETWORK OPERATIONS AI</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="font-size:10px;color:#64748b;'
            'font-weight:700;letter-spacing:1.4px;'
            'padding:8px 0;">WORKSPACE</div>',
            unsafe_allow_html=True,
        )

        selected = st.radio(
            "Navigation",
            list(pages.keys()),
            format_func=lambda name: f"{pages[name][0]}   {name}",
            label_visibility="collapsed",
            key="ran_navigation",
        )

        st.markdown("---")
        st.markdown(
            '<div style="font-size:10px;color:#64748b;'
            'font-weight:700;letter-spacing:1.4px;'
            'padding:5px 0 10px 0;">SYSTEM</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="font-size:12px;color:#94a3b8;
            line-height:1.9;">
                <span style="color:#38bdf8;">●</span>
                API endpoint configured<br>
                <span style="color:#64748b;">●</span>
                Advisory mode enabled
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.caption("RAN Intelligence Platform")
        st.caption("Version 0.1.0")

    # Compact application header.
    icon, description = pages[selected]
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;justify-content:
        space-between;padding:4px 0 16px 0;border-bottom:
        1px solid #263244;margin-bottom:22px;">
            <div>
                <div style="font-size:11px;color:#64748b;
                letter-spacing:1px;">RAN INTELLIGENCE / WORKSPACE</div>
                <div style="font-size:21px;font-weight:700;
                color:#f1f5f9;margin-top:4px;">{selected}</div>
            </div>
            <div style="font-size:12px;color:#94a3b8;">
                {description}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if selected == "Overview":
        overview()
    elif selected == "Telecom Knowledge":
        telecom_rag()
    elif selected == "Architecture":
        architecture()
    else:
        context = load_context()

        if selected == "KPI Explorer":
            kpi_explorer(context)
        elif selected == "Anomaly Detection":
            anomaly_detection(context)
        elif selected == "Forecasting":
            forecasting(context)
        elif selected == "Incident Investigation":
            incident_investigation(context)


if __name__ == "__main__":
    main()
