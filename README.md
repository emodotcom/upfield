# Upfield — Uptime & Health Checker

> Monitor your URLs. Get notified instantly when they go down.

[![CI](https://github.com/YOUR_USERNAME/upfield/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/upfield/actions/workflows/ci.yml)

---

## Features

- 🌐 HTTP/HTTPS health monitoring with configurable intervals
- 📊 Uptime percentage & response time history
- 🔔 Instant alerts via **Telegram** and **Email (SMTP)**
- 🔁 3-strike rule: alerts after 3 consecutive failures
- ✅ Recovery notifications when a site comes back up
- 🐳 Fully Dockerized (Docker Compose)
- ⚙️ GitHub Actions CI/CD pipeline
- 🚀 Deployed on Oracle Cloud Always Free (ARM VM)

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, aiohttp |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | React, TypeScript, Vite, Tailwind CSS, Recharts |
| Infrastructure | Docker, nginx, GitHub Actions, Oracle Cloud |

## Getting Started

### Prerequisites
- Python 3.12+
- Docker & Docker Compose (optional)

### 1. Clone & configure

```bash
git clone https://github.com/YOUR_USERNAME/upfield.git
cd upfield
cp .env.example .env
# Edit .env — add your Telegram token and SMTP credentials
```

### 2. Run locally (without Docker)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit **http://localhost:8000/docs** for the interactive API.

### 3. Run with Docker Compose

```bash
docker compose up -d
```

Backend: **http://localhost:8000**  
Swagger docs: **http://localhost:8000/docs**

## Environment Variables

See [`.env.example`](.env.example) for the full list with setup instructions.

Key variables:

| Variable | Description |
|---|---|
| `DATABASE_URL` | SQLite (dev) or PostgreSQL connection string |
| `TELEGRAM_BOT_TOKEN` | From @BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram chat/group ID |
| `SMTP_USER` / `SMTP_PASS` | Gmail credentials (App Password) |
| `ALERT_EMAIL` | Who receives email alerts |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/monitors/` | List all monitors |
| `POST` | `/monitors/` | Add a new monitor |
| `GET` | `/monitors/{id}` | Monitor details |
| `PUT` | `/monitors/{id}` | Update monitor |
| `DELETE` | `/monitors/{id}` | Delete monitor |
| `POST` | `/monitors/{id}/check` | Trigger immediate check |
| `GET` | `/monitors/{id}/checks` | Check history |
| `GET` | `/monitors/{id}/stats?days=7` | Uptime stats |
| `GET` | `/health` | Service liveness |

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## License

MIT
