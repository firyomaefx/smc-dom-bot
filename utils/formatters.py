"""SMC DOM Bot — Utils / Formatters.

Reusable number, date, and display formatting helpers
shared across all Streamlit pages.
"""
from datetime import datetime, timezone


def fmt_price(val, decimals=2):
    """Format a price with dollar sign and commas."""
    if val is None:
        return "$0.00"
    return f"${float(val):,.{decimals}f}"


def fmt_pnl(val, decimals=2):
    """Format P&L with sign and dollar sign."""
    if val is None:
        return "$0.00"
    v = float(val)
    sign = "+" if v >= 0 else ""
    return f"{sign}${v:,.{decimals}f}"


def fmt_pnl_color(val):
    """Return CSS color string for P&L values."""
    if val is None or float(val) >= 0:
        return "#22c55e"
    return "#ef4444"


def fmt_pct(val, decimals=1):
    """Format a percentage value."""
    if val is None:
        return "0%"
    return f"{float(val):.{decimals}f}%"


def fmt_r(val, decimals=2):
    """Format a risk-multiple (R) value."""
    if val is None:
        return "0.00R"
    v = float(val)
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.{decimals}f}R"


def fmt_myt():
    """Return current Malaysia time (GMT+8) formatted."""
    from datetime import timezone, timedelta
    myt = timezone(timedelta(hours=8))
    return datetime.now(myt).strftime("%Y-%m-%d %H:%M:%S MYT")


def fmt_utc():
    """Return current UTC time formatted."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def fmt_duration(seconds):
    """Format a duration in human-readable form."""
    if seconds is None:
        return "0s"
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m {s % 60}s"
    return f"{s // 3600}h {(s % 3600) // 60}m"


def fmt_large_number(val):
    """Format large numbers with K/M/B suffixes."""
    if val is None:
        return "0"
    v = float(val)
    if abs(v) >= 1e9:
        return f"{v/1e9:.1f}B"
    if abs(v) >= 1e6:
        return f"{v/1e6:.1f}M"
    if abs(v) >= 1e3:
        return f"{v/1e3:.1f}K"
    return f"{v:.2f}"


def grade_color(grade):
    """Return CSS color for signal grade A/B/C/F."""
    return {"A": "#22c55e", "B": "#3b82f6", "C": "#f59e0b", "F": "#ef4444"}.get(grade, "#6b7280")


def regime_color(regime):
    """Return CSS color for market regime."""
    return {
        "TRENDING": "#22c55e", "RANGING": "#f59e0b",
        "CHOPPY": "#ef4444", "QUIET": "#6b7280"
    }.get(regime, "#6b7280")


def direction_emoji(direction):
    """Return emoji for trade direction."""
    return "🟢" if direction == "BUY" else "🔴" if direction == "SELL" else "⚪"


def mask_secret(val, show=4):
    """Mask a secret value for display."""
    if not val:
        return "not set"
    if len(val) <= show:
        return "*" * len(val)
    return val[:show] + "*" * (len(val) - show)
