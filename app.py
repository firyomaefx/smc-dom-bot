"""SMC DOM Bot — Streamlit Monitoring Dashboard.

Read-only UI that polls the separately running Flask bot API.
Displays real-time SMC signals, DOM analysis, account metrics,
and alert logs. Never modifies positions (except emergency close).

Architecture: Streamlit UI → HTTP poll → Flask bot (activity_meter.py)
"""
import streamlit as st
import os, time
from datetime import datetime

st.set_page_config(
    page_title="SMC DOM Bot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from api.flask_client import (
    FLASK_API_URL, health_check, get_full_state,
    get_account, get_performance, get_signals, get_dom_data,
    get_sessions, get_health, get_logs, close_all,
)

# ── Auto-refresh every N seconds ──
REFRESH_SECS = st.sidebar.slider("Refresh interval (s)", 5, 60, 10, 5)

# ═══ TOP BAR ═══
col_l, col_m, col_r = st.columns([2, 1, 1])
with col_l:
    st.markdown("## 📊 SMC DOM Bot — Live Monitor")
with col_m:
    alive, latency = health_check()
    if alive:
        st.markdown(f"🟢 **Connected** — {latency}ms")
    else:
        st.markdown(f"🔴 **Offline** — cannot reach Flask API")
with col_r:
    st.caption(f"API: `{FLASK_API_URL}`")

# ═══ METRIC ROW ═══
state = get_full_state()
acc = state.get("account", {})
perf = state.get("performance", {})
price = state.get("price", {})

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Balance", f"${acc.get('balance', 0):,.2f}")
c2.metric("Equity", f"${acc.get('equity', 0):,.2f}")
c3.metric("Day P&L", f"${perf.get('daily_pnl', 0):.2f}",
          delta=f"{perf.get('win_rate', 0)}% WR" if perf.get('win_rate') else None)
c4.metric("Open Pos", state['positions'].__len__() if 'positions' in state else 0)
c5.metric("Regime", state.get("regime", "?"))
c6.metric("Session", state.get("session", "?"))

# ═══ PRICE TICKER ═══
if price:
    spread = state.get("spread", 0)
    st.markdown(
        f"**Bid:** <span style='color:#22c55e'>${price.get('bid', 0)}</span> &nbsp;|&nbsp; "
        f"**Ask:** <span style='color:#ef4444'>${price.get('ask', 0)}</span> &nbsp;|&nbsp; "
        f"**Spread:** ${spread:.2f}",
        unsafe_allow_html=True,
    )

st.divider()

# ═══ MAIN PANELS ═══
tab1, tab2, tab3, tab4 = st.tabs(["📡 Signals", "📊 DOM Analysis", "🏦 Account", "⚠️ Alerts"])

# ── TAB 1: Signals ──
with tab1:
    if state.get("_empty"):
        st.warning("⚠️ Flask bot offline — no signal data available")
    else:
        st.subheader("Live Signal Feed")
        signals_data = get_signals(20)
        if isinstance(signals_data, list) and signals_data:
            import pandas as pd
            df = pd.DataFrame(signals_data)
            cols = ["timestamp", "direction", "entry_price", "tp1", "tp2", "sl", "quality_score", "grade", "confidence"]
            show = [c for c in cols if c in df.columns]
            st.dataframe(df[show], use_container_width=True, height=300)
        else:
            st.info("No signals recorded yet — waiting for bot trades.")

# ── TAB 2: DOM Analysis ──
with tab2:
    st.subheader("Orderbook Depth (iTick / Dukascopy)")
    dom = get_dom_data()
    if dom.get("_empty"):
        st.warning("⚠️ DOM data unavailable")
    elif dom.get("error"):
        st.error(dom.get("error"))
    else:
        dom_left, dom_right = st.columns([2, 1])
        with dom_left:
            metrics = dom.get("metrics", {})
            direction = metrics.get("direction", "NEUTRAL")
            ratio = metrics.get("imbalance_ratio", 1.0)
            strength = metrics.get("strength", 0)
            absorption = metrics.get("absorption", False)

            direction_color = "#22c55e" if direction == "BULLISH" else "#ef4444" if direction == "BEARISH" else "#f59e0b"
            st.markdown(f"**Direction:** <span style='color:{direction_color}'>{direction}</span> | **Ratio:** {ratio}x | **Strength:** {strength}%", unsafe_allow_html=True)

            if absorption:
                st.success(f"🛡️ Absorption detected — {metrics.get('absorption_side', '?')} side")
            else:
                st.info("No significant absorption detected")

        with dom_right:
            spoof = dom.get("spoof", {})
            bid_wall = spoof.get("bid_wall", "?")
            ask_wall = spoof.get("ask_wall", "?")
            st.metric("Bid Wall Quality", bid_wall)
            st.metric("Ask Wall Quality", ask_wall)

        # Depth visualisation
        bids = dom.get("bids", [])
        asks = dom.get("asks", [])
        if bids or asks:
            st.subheader("DOM Ladder")
            import plotly.graph_objects as go
            fig = go.Figure()

            bid_prices = [b["price"] for b in bids[:8]]
            bid_vols = [b.get("volume", 0) for b in bids[:8]]
            ask_prices = [a["price"] for a in asks[:8]]
            ask_vols = [a.get("volume", 0) for a in asks[:8]]

            fig.add_trace(go.Bar(y=bid_prices, x=bid_vols, orientation="h", name="Bids", marker_color="#22c55e"))
            fig.add_trace(go.Bar(y=ask_prices, x=ask_vols, orientation="h", name="Asks", marker_color="#ef4444"))

            fig.update_layout(barmode="group", height=300, margin=dict(l=10, r=10, t=10, b=10),
                              template="plotly_dark", xaxis_title="Volume", yaxis_title="Price")
            st.plotly_chart(fig, use_container_width=True)

# ── TAB 3: Account ──
with tab3:
    st.subheader("MT5 Account")
    mt5_data = get_account()
    if mt5_data.get("_empty"):
        st.warning("⚠️ Account data unavailable")
    else:
        ac1, ac2, ac3, ac4 = st.columns(4)
        ac1.metric("Balance", f"${mt5_data.get('balance', 0):,.2f}")
        ac2.metric("Equity", f"${mt5_data.get('equity', 0):,.2f}")
        ac3.metric("Free Margin", f"${mt5_data.get('free_margin', 0):,.2f}")
        ac4.metric("Float P&L", f"${mt5_data.get('pos_pnl', 0):.2f}")

        positions = mt5_data.get("positions", [])
        if positions:
            st.subheader(f"Open Positions ({len(positions)})")
            import pandas as pd
            pos_df = pd.DataFrame(positions)
            st.dataframe(pos_df, use_container_width=True, height=200)

    # Performance
    st.subheader("Performance")
    perf_data = get_performance()
    if not perf_data.get("_empty"):
        pe1, pe2, pe3, pe4 = st.columns(4)
        pe1.metric("Daily P&L", f"${perf_data.get('daily_pnl', 0):.2f}")
        pe2.metric("Win Rate", f"{perf_data.get('win_rate', 0)}%")
        pe3.metric("Weekly P&L", f"${perf_data.get('weekly_pnl', 0):.2f}")
        pe4.metric("Kelly Fraction", f"{state.get('kelly', 0):.2f}")

    # Session breakdown
    st.subheader("Session Performance (30 days)")
    sessions = get_sessions()
    if not sessions.get("_empty") and sessions:
        import pandas as pd
        sess_df = pd.DataFrame([
            {"Session": s, **v} for s, v in sessions.items()
        ])
        st.dataframe(sess_df, use_container_width=True, height=150)

# ── TAB 4: Alerts ──
with tab4:
    st.subheader("System Alerts & Logs")
    logs = get_logs(30)
    if logs.get("_empty"):
        st.warning("⚠️ Log data unavailable")
    else:
        lines = logs.get("lines", [])
        if lines:
            log_text = "\n".join(lines[-25:])
            st.code(log_text, language="text", line_numbers=False)
        else:
            st.info("No log entries yet.")

    # Kill switch status
    ks = state.get("kill_switch", {})
    if ks.get("active"):
        st.error(f"🚫 KILL SWITCH ACTIVE: {ks.get('reason', 'Unknown')}")
    else:
        st.success("✅ All systems safe — kill switch inactive")

    # Emergency close
    st.divider()
    st.subheader("🛑 Emergency Actions")
    st.warning("⚠️ WARNING: These actions are irreversible and affect real money.")
    if st.button("🛑 CLOSE ALL POSITIONS", type="secondary", use_container_width=True):
        st.session_state["confirm_close"] = True
    if st.session_state.get("confirm_close"):
        st.error("ARE YOU SURE? This will close ALL open positions on MT5.")
        cnf1, cnf2 = st.columns(2)
        with cnf1:
            if st.button("✅ YES — CLOSE ALL", type="primary", use_container_width=True):
                result = close_all()
                st.session_state["confirm_close"] = False
                if result.get("closed", 0) > 0:
                    st.success(f"Closed {result['closed']} positions")
                else:
                    st.error(result.get("message", "Failed"))
        with cnf2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state["confirm_close"] = False

# ═══ FOOTER ═══
st.divider()
col_f1, col_f2 = st.columns([3, 1])
with col_f1:
    st.caption(f"Flask API: {FLASK_API_URL} | Auto-refresh: {REFRESH_SECS}s | Last update: {datetime.now().strftime('%H:%M:%S')}")
with col_f2:
    st.caption("Streamlit UI v1.0.0 | MIT License")

# Auto-refresh using native Streamlit rerun
time.sleep(REFRESH_SECS)
st.rerun()
