"""SMC DOM Bot — Signals Page.

Live SMC signal feed with entry/SL/TP display and quality scores.
Reads from Flask API via flask_client.
"""
import streamlit as st
from api.flask_client import get_full_state, get_signals
from utils.formatters import fmt_price, fmt_pnl, fmt_pct, grade_color, direction_emoji
import pandas as pd

st.set_page_config(page_title="Signals — SMC DOM Bot", page_icon="📡", layout="wide")

st.title("📡 Live Signal Feed")

state = get_full_state()
signals = get_signals(50)

if signals.get("_empty"):
    st.warning("⚠️ Flask bot offline — no signal data")
    st.stop()

if isinstance(signals, list) and signals:
    df = pd.DataFrame(signals)

    # Quality distribution chart
    qb_col1, qb_col2 = st.columns(2)
    with qb_col1:
        st.subheader("Signal Quality Distribution")
        q_dist = state.get("quality_distribution", {"A": 0, "B": 0, "C": 0, "F": 0})
        import plotly.graph_objects as go
        fig = go.Figure(go.Bar(
            x=list(q_dist.keys()),
            y=list(q_dist.values()),
            marker_color=[grade_color(g) for g in q_dist.keys()],
            text=list(q_dist.values()),
            textposition="outside",
        ))
        fig.update_layout(template="plotly_dark", height=250, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with qb_col2:
        st.subheader("Confidence vs Quality Score")
        if "confidence" in df.columns and "quality_score" in df.columns:
            sc = go.Figure()
            sc.add_trace(go.Scatter(y=df["confidence"].tail(30), name="Confidence", mode="lines+markers"))
            sc.add_trace(go.Scatter(y=df["quality_score"].tail(30), name="Quality", mode="lines+markers"))
            sc.update_layout(template="plotly_dark", height=250, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(sc, use_container_width=True)

    # Signal table
    st.subheader(f"Recent Signals ({len(signals)})")
    cols = ["timestamp", "direction", "entry_price", "tp1", "tp2", "sl", "grade", "quality_score", "confidence"]
    show = [c for c in cols if c in df.columns]
    st.dataframe(df[show].tail(20), use_container_width=True, height=400)
else:
    st.info("No signals recorded yet — waiting for trading bot activity.")
