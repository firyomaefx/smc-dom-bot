"""SMC DOM Bot — Account Page.

MT5 account metrics, open positions, performance charts.
"""
import streamlit as st
from api.flask_client import get_full_state, get_account, get_performance, get_sessions
from utils.formatters import fmt_price, fmt_pnl, fmt_pct, fmt_r

st.set_page_config(page_title="Account — SMC DOM Bot", page_icon="🏦", layout="wide")

st.title("🏦 Account Overview")

state = get_full_state()
mt5 = get_account()
perf = get_performance()

if mt5.get("_empty"):
    st.warning("⚠️ Flask bot offline — account data unavailable")
    st.stop()

# Account summary
ac1, ac2, ac3, ac4, ac5 = st.columns(5)
ac1.metric("Balance", fmt_price(mt5.get("balance", 0)))
ac2.metric("Equity", fmt_price(mt5.get("equity", 0)))
ac3.metric("Free Margin", fmt_price(mt5.get("free_margin", 0)))
ac4.metric("Float P&L", fmt_pnl(mt5.get("pos_pnl", 0)))
ac5.metric("Leverage", "8888x")

st.divider()

# Open positions
positions = mt5.get("positions", [])
if positions:
    st.subheader(f"📈 Open Positions ({len(positions)})")
    import pandas as pd
    pos_df = pd.DataFrame(positions)
    pos_df["direction"] = pos_df["direction"].apply(lambda x: f"🟢 {x}" if x == "BUY" else f"🔴 {x}")
    pos_df["pnl"] = pos_df["pnl"].apply(fmt_pnl)
    st.dataframe(pos_df, use_container_width=True, height=200)

# Performance
st.divider()
st.subheader("Performance")

if not perf.get("_empty"):
    pe1, pe2, pe3, pe4, pe5 = st.columns(5)
    pe1.metric("Daily Trades", perf.get("daily_trades", 0))
    pe2.metric("Daily P&L", fmt_pnl(perf.get("daily_pnl", 0)))
    pe3.metric("Win Rate", fmt_pct(perf.get("win_rate", 0)))
    pe4.metric("Weekly P&L", fmt_pnl(perf.get("weekly_pnl", 0)))
    pe5.metric("Expectancy", fmt_r(state.get("performance", {}).get("expectancy_r", 0)))

    # Recovery & Kelly
    rec = state.get("recovery", {})
    r1, r2, r3 = st.columns(3)
    r1.metric("Recovery Lot Mult", f"{rec.get('lot_mult', 1.0):.1f}x")
    r2.metric("Kelly Fraction", f"{state.get('kelly', 1.0):.2f}")
    r3.metric("Consecutive Losses", rec.get("consecutive_losses", 0))

# Session breakdown
st.divider()
st.subheader("Session Performance (30 days)")
sessions = get_sessions()
if not sessions.get("_empty") and sessions:
    import pandas as pd
    sess_data = [{"Session": s, **v} for s, v in sessions.items()]
    sess_df = pd.DataFrame(sess_data)
    st.dataframe(sess_df, use_container_width=True, height=200)
