"""RAN Intelligence Platform — Signal Lab Streamlit application."""

from datetime import UTC, date, datetime, time

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

# ---------------------------------------------------------------------------
# Signal Lab visual system
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg: #0b1118;
        --sidebar: #0d151e;
        --surface: #121e29;
        --surface-2: #172633;
        --surface-3: #1c3040;
        --border: #263b4b;
        --text: #edf5f7;
        --muted: #91a6b5;
        --teal: #39d6c3;
        --blue: #55b9ed;
        --amber: #f5bd65;
        --red: #f17e83;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 75% 0%, rgba(35, 103, 118, .12), transparent 35%),
            var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(11, 17, 24, .92);
        border-bottom: 1px solid rgba(57, 214, 195, .10);
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1540px;
        padding: 1.5rem 2.2rem 3rem;
    }

    [data-testid="stSidebar"] {
        background: var(--sidebar);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.1rem;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--muted);
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 9px;
        padding: 8px 10px;
        transition: background .18s ease, border-color .18s ease;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: var(--surface-2);
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--text) !important;
        letter-spacing: -.035em;
        font-weight: 650 !important;
    }

    h1 { font-size: 2.15rem !important; line-height: 1.2 !important; }
    h2 { font-size: 1.45rem !important; }
    h3 { font-size: 1.1rem !important; }
