# Upfield — Uptime & Health Checker

> Monitor your URLs. Get notified instantly when they go down.

[![CI](https://github.com/emodotcom/upfield/actions/workflows/ci.yml/badge.svg)](https://github.com/emodotcom/upfield/actions/workflows/ci.yml)

---

## Features

- HTTP/HTTPS health monitoring with configurable intervals
- Uptime percentage and response time history tracking
- Instant alerts via Telegram and Email (SMTP)
- 3-strike rule: alerts after 3 consecutive failures to prevent false positives
- Recovery notifications when a service is restored
- Fully Containerized (Docker & Docker Compose)
- Automated CI/CD pipelines (GitHub Actions)
- Secure environment variable management

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, aiohttp |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | React, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| Infrastructure | Docker, GitHub Actions |

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker & Docker Compose (optional for production)

### 1. Clone & Configure

```bash
git clone https://github.com/emodotcom/upfield.git
cd upfield
cp .env.example .env
# Edit .env — add your Telegram token and SMTP credentials
```

### 2. Run Locally (Development)

**Start the Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
*API Docs: http://localhost:8000/docs*

**Start the Frontend:**
```bash
cd frontend
npm install
npm run dev
```
*Dashboard: http://localhost:5173*

### 3. Run with Docker (Production)

```bash
docker compose up -d --build
```

## Environment Variables

See [`.env.example`](.env.example) for the full list with setup instructions.

## License

This project is licensed under the [MIT License](LICENSE).
