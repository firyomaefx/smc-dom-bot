# Changelog

All notable changes to the smc-dom-bot Streamlit UI are documented here.

This project follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- _(future features go here)_

### Fixed
- _(future fixes go here)_

### Changed
- _(future changes go here)_

---

## [v1.0.0] — 2026-05-09

### Added
- Initial Streamlit monitoring dashboard for SMC DOM trading bot
- Live SMC signal feed from Flask API with entry, SL, TP, and quality scores
- DOM absorption, iceberg order wall, stop hunt, and sweep detection panels
- DOM ladder visualization with bid/ask volume bars (Plotly)
- MT5 account metrics — balance, equity, free margin, floating P&L, open positions
- Per-session performance breakdown: Asia, London, New York, Overlap (30 days)
- Kill switch and recovery mode status indicators with live alerts
- Telegram alert log viewer with color-coded log terminal
- Graceful offline mode — shows clear warnings when Flask bot is unreachable
- Auto-refresh system (10 seconds default, configurable via sidebar slider)
- `flask_client.py` — typed API client with 5s timeout and error handling
- Multi-page Streamlit layout: Signals, DOM Analysis, Account, Alerts
- Emergency close button with two-step confirmation dialog
- Dark theme config matching trading dashboard aesthetic
- Comprehensive README with setup, architecture, and deployment instructions

### Fixed
- Initial release — no prior fixes

### Breaking changes
- None (initial release)

### Upgrade notes
- Clone the repo and run `pip install -r requirements.txt`
- Requires separately running Flask bot (`activity_meter.py`) with API exposed
- Set `FLASK_API_URL` in `.env` or Streamlit Cloud secrets
