"""SMC DOM Bot — Alerts Page.

System health, kill switch status, Telegram alert log, log viewer.
"""
import streamlit as st
from api.flask_client import get_full_state, get_logs, get_health, close_all
from utils.formatters import fmt_myt

st.set_page_config(page_title="Alerts — SMC DOM Bot", page_icon="⚠️", layout="wide")

st.title("⚠️ System Alerts & Monitoring")

state = get_full_state()
health = get_health()
logs = get_logs(50)

# ── Health Checks ──
st.subheader("System Health")
if not health.get("_empty"):
    items = []
    for name, data in health.items():
        if isinstance(data, dict):
            connected = data.get("connected", False)
            latency = data.get("latency_ms", 0)
            icon = "🟢" if connected else "🔴"
            items.append(f"{icon} **{name}** — {latency}ms" if connected else f"{icon} **{name}** — OFFLINE")
    
    if items:
        st.markdown("\n\n".join(items))
    else:
        st.info("Waiting for health data...")

st.divider()

# ── Kill Switch ──
ks = state.get("kill_switch", {})
if ks.get("active"):
    st.error(f"🚫 **KILL SWITCH ACTIVE** — {ks.get('reason', 'Unknown reason')}")
    st.warning("Bot has stopped trading. Investigate and resolve before restarting.")
else:
    st.success("✅ **Kill switch inactive** — bot is trading normally")

# Recovery state
rec = state.get("recovery", {})
if rec.get("consecutive_losses", 0) >= 2:
    st.warning(f"⚠️ Recovery mode active — {rec.get('consecutive_losses')} consecutive losses, lot size: {rec.get('lot_mult', 1.0)}x")

st.divider()

# ── Log Viewer ──
st.subheader("Live Log Terminal")
if logs.get("_empty"):
    st.warning("⚠️ Log data unavailable")
else:
    lines = logs.get("lines", [])
    if lines:
        log_text = "\n".join(lines)
        st.code(log_text, language="text", line_numbers=False)
        st.caption(f"Last updated: {fmt_myt()}")
    else:
        st.info("No log entries yet.")

st.divider()

# ── Emergency Actions ──
st.subheader("🛑 Emergency Controls")
st.warning("⚠️ These actions directly affect your MT5 trading account.")
if st.button("🛑 CLOSE ALL POSITIONS", type="secondary", use_container_width=True):
    st.session_state["emergency_confirm"] = True

if st.session_state.get("emergency_confirm"):
    st.error("**FINAL CONFIRMATION**: Close ALL open positions on MT5? This cannot be undone.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ YES — Close Everything", type="primary", use_container_width=True):
            result = close_all()
            st.session_state["emergency_confirm"] = False
            if result.get("closed", 0) > 0:
                st.success(f"✅ Closed {result['closed']} positions successfully")
            else:
                st.error(f"❌ Failed: {result.get('message', 'unknown')}")
    with c2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state["emergency_confirm"] = False
