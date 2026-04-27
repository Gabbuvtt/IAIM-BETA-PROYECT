# IAIM - Sistema de Gestión de Tickets y Personal

## Overview
Web application for managing maintenance tickets and personnel for the Instituto Aeronáutico Internacional de México. Spanish-language interface with role-based access (admin, supervisor, técnico).

## Architecture
- **Frontend**: Vite + React 19 (JavaScript/JSX, not TypeScript despite README), Tailwind CSS, React Router, Axios. Located in `Frontend/`.
- **Backend**: FastAPI + SQLAlchemy + python-jose JWT. Located in `Backend/` with package layout `Backend/API/` and `Backend/Auth/Login/`.
- **Database**: Replit PostgreSQL (DATABASE_URL env var). Schema is auto-created at startup by `models.Base.metadata.create_all`.

## Replit Setup
- **Frontend workflow** (`Start application`): `cd Frontend && npm run dev` on port 5000 (webview). Vite is configured with `host: 0.0.0.0`, `allowedHosts: true`, and a proxy that forwards `/auth`, `/users`, `/tickets`, `/docs`, and `/openapi.json` to the backend at `http://localhost:8000`.
- **Backend workflow** (`Backend API`): `cd Backend && uvicorn API.main:app --host 0.0.0.0 --port 8000` (console). Bound on 0.0.0.0 so Replit can detect the port; only reached via the Vite proxy.
- All frontend API calls use **relative URLs** (no hardcoded host) so they work through the preview proxy.
- Empty `__init__.py` files added to `Backend/API/`, `Backend/Auth/`, and `Backend/Auth/Login/` so Python can import the packages.
- CORS in `Backend/API/main.py` is set to allow all origins (without credentials) for the dev proxy.

## Default Credentials
A seed admin user is inserted into the `usuarios` table:
- Email: `admin@iaim.aero`
- Password: `admin12345`
- Role: `admin`

## Deployment
Configured as an autoscale deployment that builds the frontend statically and runs the FastAPI backend, which serves both the API and the built static assets. Adjust if a different topology is needed.

## Notes / Known Items
- `Backend/API/telegram_bot.py` is an optional Telegram bot module (requires `python-telegram-bot` and `TELEGRAM_BOT_TOKEN`). It's not started by the workflow.
- Original `Backend/requirements.txt` is preserved; runtime Python deps are installed via the Replit package manager (pyproject.toml/uv.lock).
