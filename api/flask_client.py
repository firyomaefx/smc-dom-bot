"""SMC DOM Bot — Flask API Client.

Owns ALL HTTP communication between the Streamlit UI and
the separately running Flask bot (activity_meter.py).

Every function:
  - Loads FLASK_API_URL from streamlit secrets (or env for local dev)
  - Has a 5-second timeout
  - Returns empty structures on failure — never crashes the UI
  - Logs connection errors via st.warning()
"""
import requests
import streamlit as st
import os
import logging

logger = logging.getLogger(__name__)

FLASK_API_URL = st.secrets.get("FLASK_API_URL") or os.getenv("FLASK_API_URL", "http://127.0.0.1:5001")
_TIMEOUT = 5


def _get(endpoint, params=None):
    """Safe HTTP GET wrapper. Returns parsed JSON or {} on failure."""
    url = f"{FLASK_API_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    try:
        r = requests.get(url, params=params, timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        logger.warning(f"Flask bot unreachable: {url}")
        return _empty("connection_refused")
    except requests.exceptions.Timeout:
        logger.warning(f"Flask bot timeout: {url}")
        return _empty("timeout")
    except requests.exceptions.RequestException as e:
        logger.warning(f"Flask bot error: {url} — {e}")
        return _empty("error")


def _empty(reason=""):
    """Return a safe empty structure that won't crash Streamlit."""
    return {"_error": reason, "_empty": True}


def health_check():
    """Test if Flask bot is reachable. Returns (alive: bool, latency_ms: int)."""
    import time
    try:
        t0 = time.time()
        r = requests.get(f"{FLASK_API_URL.rstrip('/')}/api/state", timeout=_TIMEOUT)
        latency = int((time.time() - t0) * 1000)
        return r.ok, latency
    except Exception:
        return False, 0


def get_full_state():
    """GET /api/state — full bot state dump."""
    data = _get("api/state")
    if data.get("_empty"):
        st.warning(f"⚠️ Flask bot offline — cannot reach {FLASK_API_URL}")
    return data


def get_signals(limit=50):
    """GET /api/signals — recent trading signals."""
    return _get("api/signals", params={"limit": limit})


def get_dom_data():
    """GET /api/dom-depth — DOM orderbook analysis (Dukascopy + iTick)."""
    return _get("api/dom-depth")


def get_account():
    """GET /api/mt5 — account balance, equity, positions."""
    return _get("api/mt5")


def get_performance():
    """GET /api/stats — daily/weekly P&L, win rate."""
    return _get("api/stats")


def get_sessions():
    """GET /api/sessions — per-session performance breakdown."""
    return _get("api/sessions")


def get_health():
    """GET /api/health — all system health checks (MT5, Ollama, TG, etc.)."""
    return _get("api/health")


def get_logs(lines=50):
    """GET /api/log — recent log lines from smc_dom_bot.log."""
    return _get("api/log", params={"lines": lines})


def close_all():
    """POST /api/closeall — emergency close all positions."""
    try:
        r = requests.post(
            f"{FLASK_API_URL.rstrip('/')}/api/closeall",
            timeout=_TIMEOUT
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Emergency close failed: {e}")
        return {"closed": 0, "message": str(e)}
