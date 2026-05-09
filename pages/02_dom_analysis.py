"""SMC DOM Bot — DOM Analysis Page.

DOM absorption, iceberg, stop hunt, sweep, CVD, and volume profile.
"""
import streamlit as st
from api.flask_client import get_full_state, get_dom_data
from utils.formatters import fmt_price, fmt_pnl

st.set_page_config(page_title="DOM Analysis — SMC DOM Bot", page_icon="📊", layout="wide")

st.title("📊 DOM / Orderbook Analysis")

state = get_full_state()
dom = get_dom_data()

if dom.get("_empty"):
    st.warning("⚠️ Flask bot offline — DOM data unavailable")
    st.stop()

if dom.get("error"):
    st.error(f"DOM error: {dom['error']}")
    st.stop()

# Source info
source = dom.get("source", "unknown")
st.caption(f"Data source: **{source}** | Levels: {dom.get('levels', 0)}")

# DOM ladder
bids = dom.get("bids", [])
asks = dom.get("asks", [])

col_bids, col_spread, col_asks = st.columns([2, 1, 2])

with col_bids:
    st.subheader("🟢 Bids (Buy Orders)")
    if bids:
        import pandas as pd
        bid_df = pd.DataFrame(bids[:10])
        bid_df["price"] = bid_df["price"].apply(fmt_price)
        st.dataframe(bid_df[["price", "volume"]].rename(columns={"price": "Bid Price", "volume": "Volume"}), use_container_width=True, height=250)

with col_spread:
    st.subheader("Spread")
    if bids and asks:
        spread = asks[0]["price"] - bids[0]["price"]
        st.metric("Mid Price", fmt_price((bids[0]["price"] + asks[0]["price"]) / 2))
        st.metric("Spread", fmt_price(spread))
        st.metric("Bid Vol", f"{sum(b['volume'] for b in bids):.1f}")
        st.metric("Ask Vol", f"{sum(a['volume'] for a in asks):.1f}")

with col_asks:
    st.subheader("🔴 Asks (Sell Orders)")
    if asks:
        import pandas as pd
        ask_df = pd.DataFrame(asks[:10])
        ask_df["price"] = ask_df["price"].apply(fmt_price)
        st.dataframe(ask_df[["price", "volume"]].rename(columns={"price": "Ask Price", "volume": "Volume"}), use_container_width=True, height=250)

# DOM metrics
st.divider()
metrics = dom.get("metrics", {})
mc1, mc2, mc3, mc4 = st.columns(4)
mc1.metric("Imbalance Direction", metrics.get("direction", "NEUTRAL"))
mc2.metric("Imbalance Ratio", f"{metrics.get('imbalance_ratio', 1.0):.2f}x")
mc3.metric("Strength", f"{metrics.get('strength', 0)}%")
mc4.metric("Absorption", "✅" if metrics.get("absorption") else "❌")

# Spoof and pull/stack
spo_col1, spo_col2 = st.columns(2)
with spo_col1:
    st.subheader("Spoof Detection")
    spoof = dom.get("spoof", {})
    st.write(f"Bid Wall: **{spoof.get('bid_wall', '?')}**")
    st.write(f"Ask Wall: **{spoof.get('ask_wall', '?')}**")
    st.write(f"Spoof scans: {spoof.get('spoof_count', 0)}")

with spo_col2:
    st.subheader("Pull / Stack Detection")
    ps = dom.get("pull_stack", {})
    st.write(f"Bid Behavior: **{ps.get('bid_behavior', '?')}**")
    st.write(f"Ask Behavior: **{ps.get('ask_behavior', '?')}**")
