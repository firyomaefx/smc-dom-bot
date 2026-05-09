# smc-dom-bot

> Real-time Smart Money Concepts (SMC) DOM analysis dashboard —
> Streamlit monitoring UI for the smc-dom-bot trading system.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-app-red)
![License](https://img.shields.io/badge/License-MIT-green)

## Overview

This is the **read-only monitoring dashboard** for the SMC DOM trading bot. It polls
a separately running Flask bot (`activity_meter.py`) via HTTP API and displays live
SMC signals, DOM orderbook analysis, MT5 account metrics, and alert logs.

The Flask bot executes trades autonomously — this UI never places orders directly
(except for an emergency close button). They run as two independent processes.

## Features

- Live SMC signal feed with entry, stop loss, take profit, and quality scores
- DOM absorption, iceberg order wall, stop hunt, and sweep detection panels
- MT5 account metrics — balance, equity, free margin, open positions, floating P&L
- Per-session performance breakdown (Asia / London / New York / Overlap, 30 days)
- Kill switch and recovery mode status indicators with real-time alerts
- Telegram alert log viewer with color-coded log lines
- CVD, volume profile, and DOM ladder charts via Plotly
- Auto-refreshes every 10 seconds — no manual browser reload needed
- Graceful offline mode — shows clear warning instead of crashing when Flask is down

## Architecture

```
┌──────────────────────┐        HTTP poll         ┌──────────────────────┐
│   Streamlit UI       │ ──────────────────────→   │   Flask Bot           │
│   (this repo)        │ ←──────────────────────   │   (activity_meter)    │
│                      │        JSON responses      │                       │
│   app.py             │                            │   /api/state          │
│   pages/*            │                            │   /api/signals        │
│   flask_client.py    │                            │   /api/dom-depth      │
└──────────────────────┘                            │   /api/account        │
                                                    │   ...                 │
                                                    └───────┬───────────────┘
                                                            │
                                                            ▼
                                                    ┌───────┴───────────────┐
                                                    │   MT5 Terminal         │
                                                    │   (Mtrading-Live)      │
                                                    └───────────────────────┘
```

## Project structure

```
smc-dom-ui/
├── .streamlit/
│   ├── config.toml           # Theme, layout, server settings
│   └── secrets.toml          # ⚠ LOCAL ONLY — gitignored
├── api/
│   └── flask_client.py       # All HTTP calls to Flask bot API
├── pages/
│   ├── 01_signals.py         # Live SMC signal feed
│   ├── 02_dom_analysis.py    # DOM absorption / iceberg / sweep
│   ├── 03_account.py         # MT5 account metrics
│   └── 04_alerts.py          # Telegram alert log
├── utils/
│   └── formatters.py         # Number/date formatting helpers
├── app.py                    # Streamlit entry point
├── .env.example              # Secret keys with blank values
├── .gitignore
├── requirements.txt
├── packages.txt
├── README.md
├── CHANGELOG.md
└── LICENSE
```

## Quickstart (local)

```bash
git clone https://github.com/firyomaefx/smc-dom-bot.git
cd smc-dom-bot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # fill in your real values
streamlit run app.py
```

**Prerequisites:** The Flask bot (`activity_meter.py` in the separate `smc-dom-bot` trading project)
must be running first. Without it, this dashboard shows "Bot offline" warnings on all panels.

## Configuration

| Variable | Description | Required |
|---|---|---|
| `FLASK_API_URL` | Base URL of running Flask bot (e.g. `http://localhost:5001`) | Yes |
| `MT5_LOGIN` | MetaTrader 5 account login number | Yes |
| `MT5_PASSWORD` | MetaTrader 5 account password | Yes |
| `MT5_SERVER` | MT5 broker server name (e.g. `Mtrading-Live`) | Yes |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token for alert notifications | Optional |
| `TELEGRAM_CHAT_ID` | Telegram chat or channel ID to receive alerts | Optional |
| `OLLAMA_BASE_URL` | Ollama API base URL (default: `http://localhost:11434`) | Optional |

## Deploying to Streamlit Cloud

1. Push this repo to `github.com/firyomaefx/smc-dom-bot` (main branch)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app** → select `firyomaefx/smc-dom-bot` · branch `main` · file `app.py`
4. Under **Advanced settings** → **Secrets**, paste your config as TOML:
   ```toml
   FLASK_API_URL = "http://your-vps-ip:5001"
   MT5_LOGIN = "10046026"
   MT5_PASSWORD = "your_password"
   MT5_SERVER = "Mtrading-Live"
   TELEGRAM_BOT_TOKEN = "your_bot_token"
   TELEGRAM_CHAT_ID = "your_chat_id"
   OLLAMA_BASE_URL = "http://localhost:11434"
   ```
5. Click **Deploy** — expected build time: 2–5 minutes

⚠️ **WARNING:** `FLASK_API_URL` must point to a **publicly reachable** URL
when deployed to Streamlit Cloud. Options:

| Solution | Cost | Setup |
|---|---|---|
| Deploy Flask bot to a VPS (DigitalOcean, Hetzner) | ~$5/mo | Install project, run `python main.py --mode live` |
| **ngrok tunnel** | Free | `ngrok http 5001` → copy the `https://....ngrok.io` URL |
| Cloudflare Tunnel | Free | Install `cloudflared`, create tunnel to `localhost:5001` |
| Localhost only | Free | Works for development but NOT for Streamlit Cloud |

## Flask bot (activity_meter.py)

This repo does **NOT** contain the Flask bot source code. It is a read-only
monitoring UI. The Flask bot runs independently and exposes these endpoints:

| Endpoint | What it returns |
|---|---|
| `GET /api/state` | Full bot state (account, positions, regime, kill switch, recovery) |
| `GET /api/signals` | Recent trading signals with quality scores |
| `GET /api/dom-depth` | DOM orderbook data (Dukascopy + iTick combined) |
| `GET /api/mt5` | MT5 account with positions |
| `GET /api/stats` | Daily/weekly performance stats |
| `GET /api/sessions` | Per-session breakdown (30 days) |
| `GET /api/health` | All system health checks |
| `GET /api/log` | Live log tail |
| `POST /api/closeall` | Emergency close all positions |

If your Flask bot exposes different endpoints, update `api/flask_client.py`.

## Changelog

See [CHANGELOG.md](./CHANGELOG.md)

## License

[MIT](./LICENSE)
