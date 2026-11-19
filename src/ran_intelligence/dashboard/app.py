Put all six files in one folder and upload it.

index.html

html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Overview | RAN Intelligence Platform</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="w">
<nav><a href="index.html" style="margin:0"><b style="color:var(--ink)">RAN Intelligence</b></a><div><a href="features.html">Features</a><a href="architecture.html">Architecture</a><a href="investigation.html">Investigation</a></div></nav>
<header style="padding-top:56px">
<h1>Make sense of 5G radio networks.</h1>
<p class="lead">RAN Intelligence Platform turns raw 5G measurements into KPI insight, anomaly signals, forecasts, standards search, and AI-assisted incident reports that a person reviews before anyone acts.</p>

<div class="card demo" id="demo">
<div class="demo-top">
<div><strong>Try the anomaly detector</strong><span>A simulated SINR trace with a coverage dip. Move the slider to change how strict the detector is.</span></div>
<label class="ctl">Robust z-score threshold <input id="th" type="range" min="1" max="6" step="0.1" value="3.5" aria-label="Robust z-score threshold"><span class="read" id="thv">3.5</span></label>
</div>
<svg id="hero" viewBox="0 0 900 300" role="img" aria-label="Simulated SINR time series with flagged anomalies"></svg>
<div class="stat"><span><b id="nf">0</b> flagged observations</span><span><b id="ne">0</b> anomaly episodes</span><span>Flags are signals to investigate, not confirmed faults.</span></div>
</div>
</header>

<section><h2>Explore the platform</h2>
<div class="grid g2">
<a class="card feat link" href="features.html"><h3>Features</h3><p>KPI explorer, anomaly detection, forecast evaluation, and telecom standards search.</p><span class="tag">See the four tools ›</span></a>
<a class="card feat link" href="architecture.html"><h3>Architecture</h3><p>Data, intelligence and delivery layers, plus the technology stack.</p><span class="tag">See how it fits together ›</span></a>
<a class="card feat link" href="investigation.html"><h3>Investigation</h3><p>The agent workflow, the human review step, and the limits of the platform.</p><span class="tag">See the workflow ›</span></a>
</div></section>

<section>
<h2>Built with</h2>
<div class="stack">
<div class="card"><b>Python</b><span>pandas, scikit-learn, Plotly</span></div>
<div class="card"><b>FastAPI</b><span>REST API, request validation</span></div>
<div class="card"><b>Streamlit</b><span>Interactive dashboard</span></div>
<div class="card"><b>FAISS and BM25</b><span>Hybrid retrieval with RRF</span></div>
<div class="card"><b>LangGraph</b><span>Agent workflow, human review</span></div>
</div>
</section>
<footer>RAN Intelligence Platform, version 0.1.0. Built by Prashant Kumar Singh.</footer>
</div>
<script src="app.js"></script>
</body>
</html>

features.html

html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Features | RAN Intelligence Platform</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="w">
<nav><a href="index.html" style="margin:0"><b style="color:var(--ink)">RAN Intelligence</b></a><div><a href="features.html" class="on" aria-current="page">Features</a><a href="architecture.html">Architecture</a><a href="investigation.html">Investigation</a></div></nav>
<header class="ph"><h1>Features</h1><p class="lead">Four tools over one dataset, served through one API to one dashboard.</p></header>

<section id="capabilities">
<h2>Four tools, one dataset</h2>
<p style="margin-top:16px">Everything runs on the AERPAW 5G measurement dataset and is served through one API to one dashboard.</p>
<div class="grid g2">
<article class="card feat"><h3>KPI explorer</h3><p>Pick a session and a radio indicator, choose an interval and an aggregation, and see how signal quality moves over time.</p>
<svg viewBox="0 0 420 130" id="kpi" role="img" aria-label="KPI trend"></svg><span class="tag">Median, mean, min or max over 1 s to 1 min</span></article>
<article class="card feat"><h3>Anomaly detection</h3><p>A robust z-score flags unusual KPI values, then merges neighbouring flags into episodes so you review events, not single points.</p>
<svg viewBox="0 0 420 130" id="anom" role="img" aria-label="Anomaly episode"></svg><span class="tag">Threshold, minimum samples and episode gap are adjustable</span></article>
<article class="card feat"><h3>Forecast evaluation</h3><p>Models predict a KPI several steps ahead and are scored on a chronological holdout, with a gap between training and test data to prevent leakage.</p>
<svg viewBox="0 0 420 130" id="fc" role="img" aria-label="Actual versus predicted values"></svg><span class="tag">Actual vs predicted on unseen future time</span></article>
<article class="card feat"><h3>Telecom knowledge search</h3><p>Ask a question about 3GPP and ETSI standards. Meaning-based and keyword search run side by side and are merged into one ranked list of source passages.</p>
<div class="flow" style="margin:0;gap:6px">
<div class="node k" style="flex-basis:90px;padding:10px"><b style="font-size:14px">Question</b></div><span class="arr">›</span>
<div style="display:grid;gap:6px;flex:1 1 140px"><div class="node" style="padding:8px 10px"><b style="margin:0;font-size:13px">FAISS vectors</b></div><div class="node" style="padding:8px 10px"><b style="margin:0;font-size:13px">BM25 keywords</b></div></div><span class="arr">›</span>
<div class="node k" style="flex-basis:110px;padding:10px"><b style="font-size:14px">RRF fusion</b>ranked passages</div></div>
<span class="tag">Returns evidence passages, not a generated answer</span></article>
</div>
</section>
<footer>RAN Intelligence Platform, version 0.1.0. Built by Prashant Kumar Singh.</footer>
</div>
<script src="app.js"></script>
</body>
</html>

architecture.html

html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Architecture | RAN Intelligence Platform</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="w">
<nav><a href="index.html" style="margin:0"><b style="color:var(--ink)">RAN Intelligence</b></a><div><a href="features.html">Features</a><a href="architecture.html" class="on" aria-current="page">Architecture</a><a href="investigation.html">Investigation</a></div></nav>
<header class="ph"><h1>Architecture</h1><p class="lead">Three layers keep data, analysis and interface separate.</p></header>

<section id="architecture">
<h2>How the pieces fit</h2>
<p style="margin-top:16px">Three layers keep data, analysis and interface separate, so each can change without breaking the others.</p>
<div class="layers">
<div class="card layer"><div>Data<small>Foundation</small></div><div class="chips"><span class="chip">AERPAW 5G measurements</span><span class="chip">Ingestion <i>and</i> validation</span><span class="chip">Parquet storage</span></div></div>
<div class="card layer"><div>Intelligence<small>Services</small></div><div class="chips"><span class="chip">KPI analytics</span><span class="chip">Anomaly pipeline</span><span class="chip">Forecasting</span><span class="chip">Hybrid retrieval</span><span class="chip">LangGraph incident agent</span><span class="chip">Network digital twin</span></div></div>
<div class="card layer"><div>Delivery<small>Service and interface</small></div><div class="chips"><span class="chip">FastAPI REST endpoints with validated requests</span><span class="chip">Streamlit dashboard</span></div></div>
</div>
</section>

<section>
<h2>Built with</h2>
<div class="stack">
<div class="card"><b>Python</b><span>pandas, scikit-learn, Plotly</span></div>
<div class="card"><b>FastAPI</b><span>REST API, request validation</span></div>
<div class="card"><b>Streamlit</b><span>Interactive dashboard</span></div>
<div class="card"><b>FAISS and BM25</b><span>Hybrid retrieval with RRF</span></div>
<div class="card"><b>LangGraph</b><span>Agent workflow, human review</span></div>
</div>
</section>
<footer>RAN Intelligence Platform, version 0.1.0
You stopped Claude’s response

the format i sent, it was python

Here is a Streamlit showcase in the same format as your frontend. It’s one Python file with sidebar pages (Home, Features, Architecture, Investigation) and Plotly visuals. It uses built-in demo data, so it runs without your FastAPI backend and can be deployed on its own, for example on Streamlit Community Cloud.

showcase.py

python
"""RAN Intelligence Platform — showcase site (Streamlit).

Run:  streamlit run showcase.py
Needs: streamlit, plotly, pandas, numpy
"""

from textwrap import dedent

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="RAN Intelligence Platform",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root{--bg:#10141c;--side:#0b0f16;--card:#181f2b;--line:#293445;--text:#f1f5f9;
          --muted:#94a3b8;--blue:#38bdf8;--indigo:#818cf8;--green:#34d399;--amber:#fbbf24;--red:#fb7185;}
    html,body,[class*="css"]{font-family:'Inter',sans-serif;}
    .stApp{background:var(--bg);color:var(--text);}
    [data-testid="stHeader"]{background:rgba(16,20,28,.92);border-bottom:1px solid var(--line);}
    [data-testid="stMainBlockContainer"]{max-width:1300px;padding-top:2rem;padding-bottom:3rem;}
    [data-testid="stSidebar"]{background:var(--side);border-right:1px solid var(--line);}
    h1,h2,h3{color:var(--text)!important;letter-spacing:-.03em;font-weight:700!important;}
    p,li,label{color:#cbd5e1;}
    [data-testid="stMetric"]{background:linear-gradient(145deg,#1b2533,#151c27);
        border:1px solid var(--line);border-radius:12px;padding:18px 20px;}
    [data-testid="stMetricLabel"]{color:var(--muted)!important;}
    [data-testid="stVerticalBlockBorderWrapper"]{background:var(--card);
        border:1px solid var(--line);border-radius:12px;}
    [data-testid="stExpander"]{background:var(--card);border:1px solid var(--line);border-radius:10px;}
    .hero{background:linear-gradient(115deg,#172638,#18243a 60%,#22213d);border:1px solid #30445a;
        border-radius:16px;padding:40px 36px;margin-bottom:24px;}
    .hero .k{color:#38bdf8;font-size:12px;font-weight:700;letter-spacing:2px;margin-bottom:12px;}
    .hero .t{color:#f1f5f9;font-size:44px;font-weight:800;letter-spacing:-1.5px;line-height:1.1;max-width:760px;}
    .hero .s{color:#a9bacb;font-size:17px;margin-top:14px;max-width:700px;line-height:1.6;}
    .pill{display:inline-block;padding:5px 12px;margin:14px 8px 0 0;border-radius:99px;
        background:#123047;border:1px solid #24516d;color:#7dd3fc;font-size:12px;font-weight:600;}
    .cap-i{color:#38bdf8;font-size:24px;margin-bottom:8px;}
    .cap-t{color:#f1f5f9;font-weight:650;font-size:15px;margin-bottom:6px;}
    .cap-d{color:#94a3b8;font-size:13px;line-height:1.55;}
    .layer{background:#111925;border:1px solid #29384a;border-radius:14px;padding:18px;margin-bottom:12px;}
    .layer .h{color:#7dd3fc;font-size:11px;font-weight:700;letter-spacing:1.2px;margin-bottom:12px;}
    .chip{display:inline-block;background:#1b2939;border:1px solid #38516a;border-radius:8px;
        padding:8px 12px;margin:0 8px 8px 0;color:#f1f5f9;font-size:13px;}
    .arrow{text-align:center;color:#38bdf8;font-size:22px;margin:-4px 0 8px;}
    .step{border-left:2px solid #293445;padding:0 0 22px 22px;position:relative;}
    .step:before{content:"";position:absolute;left:-7px;top:4px;width:12px;height:12px;
        border-radius:50%;background:#38bdf8;}
    .step.review:before{background:#fbbf24;}
    .step b{color:#f1f5f9;font-size:16px;display:block;}
    .step span{color:#94a3b8;font-size:14px;}
    .flow{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:6px 0 14px;}
    .flow .n{background:#1b2939;border:1px solid #38516a;border-radius:10px;padding:10px 14px;
        color:#f1f5f9;font-size:13px;font-weight:600;}
    .flow .n.k{border-color:#38bdf8;background:#123047;}
    .flow .a{color:#38bdf8;}
    </style>
    """,
    unsafe_allow_html=True,
)

PLOT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=30, b=10),
    font=dict(family="Inter, sans-serif", color="#94A3B8"),
    hovermode="x unified",
)


def html(markup):
    st.markdown(dedent(markup), unsafe_allow_html=True)


def banner(kicker, title, sub):
    html(f"""
        <div class="hero"><div class="k">{kicker}</div>
        <div class="t">{title}</div><div class="s">{sub}</div></div>
    """)


# ---------------------------------------------------------------- demo data
@st.cache_data
def sinr_trace():
    rng = np.random.default_rng(7)
    t = np.arange(160)
    y = 18 + 4 * np.sin(t / 9) + rng.normal(0, 1.2, t.size)
    y[78:91] -= 11 + rng.uniform(0, 2, 13)  # coverage dip
    y[40:42] -= 8
    y[112] += 9
    return pd.DataFrame({"t": t, "sinr": y})


def robust_z(values):
    med = np.median(values)
    mad = 1.4826 * np.median(np.abs(values - med))
    return np.abs(values - med) / mad


def episodes(flags, gap=2):
    found = []
    for i in np.flatnonzero(flags):
        if found and i - found[-1][1] <= gap + 1:
            found[-1][1] = i
        else:
            found.append([i, i])
    return found


def anomaly_figure(df, threshold):
    z = robust_z(df["sinr"].to_numpy())
    flags = z >= threshold
    fig = go.Figure()
    for a, b in episodes(flags):
        fig.add_vrect(x0=a - 1, x1=b + 1, fillcolor="#fb7185", opacity=0.14, line_width=0)
    fig.add_trace(go.Scatter(x=df["t"], y=df["sinr"], mode="lines", name="SINR (dB)",
                             line=dict(color="#38BDF8", width=2.4)))
    fig.add_trace(go.Scatter(x=df["t"][flags], y=df["sinr"][flags], mode="markers",
                             name="Flagged", marker=dict(color="#fb7185", size=8)))
    fig.update_layout(height=360, xaxis_title="Time (s)", yaxis_title="SINR (dB)", **PLOT)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(148,163,184,.12)")
    return fig, int(flags.sum()), len(episodes(flags))


def forecast_figure():
    t = np.arange(140)
    actual = np.sin(t / 8) + 0.35 * np.sin(t / 3)
    pred = np.r_[actual[:3], 0.9 * actual[:-3]] + 0.1 * np.r_[actual[:6], actual[:-6]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=actual, name="Actual", line=dict(color="#38BDF8", width=2.4)))
    fig.add_trace(go.Scatter(x=t, y=pred, name="Predicted",
                             line=dict(color="#818CF8", width=2.4, dash="dash")))
    fig.add_vrect(x0=112, x1=139, fillcolor="#fbbf24", opacity=0.08, line_width=0,
                  annotation_text="Test window", annotation_font_color="#fbbf24")
    fig.update_layout(height=320, xaxis_title="Step", yaxis_title="Normalised KPI", **PLOT)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(148,163,184,.12)")
    return fig


# ------------------------------------------------------------------- pages
def home():
    banner(
        "NETWORK INTELLIGENCE · 5G RAN",
        "Make sense of 5G radio networks.",
        "KPI analytics, anomaly signals, forecasts, standards search and AI-assisted "
        "incident investigation, with a person reviewing every report.",
    )
    html("""
        <span class="pill">FastAPI</span><span class="pill">Streamlit</span>
        <span class="pill">FAISS + BM25</span><span class="pill">LangGraph</span>
        <span class="pill">AERPAW 5G data</span>
    """)

    st.markdown("### Try the anomaly detector")
    st.caption("A simulated SINR trace with a coverage dip. Raise the threshold to make the detector stricter.")
    threshold = st.slider("Robust z-score threshold", 1.0, 6.0, 3.5, 0.1)
    fig, flagged, n_events = anomaly_figure(sinr_trace(), threshold)
    c1, c2, c3 = st.columns(3)
    c1.metric("Observations", f"{len(sinr_trace()):,}")
    c2.metric("Flagged observations", flagged)
    c3.metric("Anomaly episodes", n_events)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Flags are signals to investigate, not confirmed network faults.")

    st.divider()
    st.markdown("### What the platform does")
    caps = [
        ("◈", "KPI analytics", "Explore radio measurements and time series by session and interval."),
        ("⌁", "Anomaly detection", "Flag unusual KPI values and group them into episodes."),
        ("↗", "Forecasting", "Score models on a chronological holdout with a leakage gap."),
        ("⌕", "Telecom knowledge", "Hybrid search across indexed 3GPP and ETSI documents."),
        ("◎", "Incident investigation", "An agent collects evidence and drafts an advisory report."),
        ("◇", "Human review", "A reviewer approves or rejects every report."),
        ("△", "Network simulation", "Simplified 5G NR scenarios for what-if analysis."),
        ("⌘", "Observability", "Evaluation checks and investigation traces."),
    ]
    cols = st.columns(4, gap="medium")
    for i, (icon, title, text) in enumerate(caps):
        with cols[i % 4].container(border=True):
            html(f'<div class="cap-i">{icon}</div><div class="cap-t">{title}</div>'
                 f'<div class="cap-d">{text}</div>')


def features():
    banner("FEATURES", "Four tools over one dataset",
           "Everything runs on the AERPAW 5G measurements and is served through a single API.")

    st.markdown("### KPI explorer")
    left, right = st.columns([1, 2], gap="large")
    with left:
        st.write("Choose an aggregation interval and method to see how the same signal looks at different resolutions.")
        interval = st.selectbox("Aggregation interval", ["1s", "5s", "10s", "30s"], index=1)
        method = st.selectbox("Aggregation method", ["median", "mean", "min", "max"])
    with right:
        rng = np.random.default_rng(3)
        idx = pd.date_range("2023-09-15 11:30", periods=600, freq="s")
        raw = pd.Series(18 + 4 * np.sin(np.arange(600) / 60) + rng.normal(0, 1.5, 600), index=idx)
        agg = raw.resample(interval).agg(method)
        fig = go.Figure(go.Scatter(x=agg.index, y=agg.values, line=dict(color="#38BDF8", width=2.4),
                                   fill="tozeroy", fillcolor="rgba(56,189,248,.08)"))
        fig.update_layout(height=300, yaxis_title="SINR (dB)", **PLOT)
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="rgba(148,163,184,.12)")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("### Forecast evaluation")
    left, right = st.columns([1, 2], gap="large")
    left.write("Models predict a KPI several steps ahead and are scored on a chronological holdout. "
               "A gap between training and test data prevents leakage.")
    left.caption("Illustrative curves, not real model output.")
    right.plotly_chart(forecast_figure(), use_container_width=True)

    st.divider()
    st.markdown("### Telecom knowledge search")
    st.write("Meaning-based (FAISS) and keyword (BM25) search run side by side. "
             "Reciprocal rank fusion merges them into one ranked list of source passages.")
    html("""
        <div class="flow"><div class="n k">Question</div><span class="a">›</span>
        <div class="n">FAISS vector rank</div><span class="a">+</span><div class="n">BM25 keyword rank</div>
        <span class="a">›</span><div class="n k">RRF fusion</div><span class="a">›</span>
        <div class="n k">Ranked passages</div></div>
    """)
    k = st.slider("RRF constant k", 1, 100, 60)
    rows = [("Passage A", 1, 3), ("Passage B", 2, 1), ("Passage C", 5, 2), ("Passage D", 3, 6)]
    table = pd.DataFrame(
        [{"Passage": n, "Vector rank": v, "BM25 rank": b, "RRF score": 1 / (k + v) + 1 / (k + b)}
         for n, v, b in rows]
    ).sort_values("RRF score", ascending=False)
    table["Fused rank"] = range(1, len(table) + 1)
    st.dataframe(table.style.format({"RRF score": "{:.5f}"}), hide_index=True, use_container_width=True)
    st.caption("Illustrative ranks. Search returns evidence passages, not a generated answer.")


def architecture():
    banner("ARCHITECTURE", "From raw measurements to actionable intelligence",
           "Three layers keep data, analysis and interface separate.")
    html("""
        <div class="layer"><div class="h">DATA FOUNDATION</div>
        <span class="chip">AERPAW 5G measurements</span><span class="chip">Ingestion and validation</span>
        <span class="chip">Parquet storage</span></div>
        <div class="arrow">↓</div>
        <div class="layer"><div class="h">INTELLIGENCE SERVICES</div>
        <span class="chip">KPI analytics</span><span class="chip">Anomaly pipeline</span>
        <span class="chip">Forecasting</span><span class="chip">Hybrid retrieval (FAISS + BM25 + RRF)</span>
        <span class="chip">LangGraph incident agent</span><span class="chip">Network digital twin</span></div>
        <div class="arrow">↓</div>
        <div class="layer"><div class="h">SERVICE AND PRESENTATION</div>
        <span class="chip">FastAPI REST endpoints with validated requests</span>
        <span class="chip">Streamlit dashboard</span></div>
    """)

    st.markdown("### Technology stack")
    stack = [("Python", "pandas, scikit-learn, Plotly"), ("FastAPI", "REST API, validation"),
             ("Streamlit", "Interactive dashboard"), ("FAISS + BM25", "Hybrid retrieval"),
             ("LangGraph", "Agent workflow")]
    cols = st.columns(len(stack))
    for col, (name, text) in zip(cols, stack):
        with col.container(border=True):
            st.markdown(f"**{name}**")
            st.caption(text)


def investigation():
    banner("INCIDENT INVESTIGATION", "Investigations a person signs off",
           "An agent gathers evidence and drafts an advisory report. Nothing is approved without a reviewer.")
    html("""
        <div class="step"><b>Describe the incident</b>
        <span>Session, time window, severity, optional cell and suspected KPIs.</span></div>
        <div class="step"><b>Agent collects evidence</b>
        <span>Tools pull measurements, anomaly signals and relevant standards passages.</span></div>
        <div class="step"><b>Report is drafted</b>
        <span>Summary, hypotheses tied to evidence, limitations and recommended actions.
        Hypotheses without evidence references are dropped.</span></div>
        <div class="step review"><b>Human review</b>
        <span>The reviewer approves or rejects the report and can leave feedback.</span></div>
    """)

    st.markdown("### What it does not claim")
    for title, text in [
        ("Small dataset", "The AERPAW data holds two short sessions, so forecast scores do not show "
                          "how models perform on unseen sessions."),
        ("Anomalies are not faults", "Flags are statistical signals. Confirming a fault needs supporting "
                                     "evidence and review."),
        ("Simplified simulation", "The digital twin is a simplified model, not a 3GPP-compliant "
                                  "link-level simulator."),
        ("Advisory only", "The platform never controls live network infrastructure."),
    ]:
        with st.expander(title):
            st.write(text)


PAGES = {"Home": home, "Features": features, "Architecture": architecture,
         "Investigation": investigation}


def main():
    with st.sidebar:
        html("""
            <div style="padding:6px 2px 18px;">
              <div style="font-size:16px;font-weight:750;color:#f1f5f9;">RAN Intelligence</div>
              <div style="font-size:10px;color:#94a3b8;letter-spacing:1.2px;">NETWORK OPERATIONS AI</div>
            </div>
        """)
        page = st.radio("Navigation", list(PAGES), label_visibility="collapsed")
        st.markdown("---")
        st.caption("Version 0.1.0 · Built by Prashant Kumar Singh")
    PAGES[page]()


if __name__ == "__main__":
    main()

Run it with streamlit run showcase.py after pip install streamlit plotly pandas numpy. I haven’t run it, so check it once before you upload.
