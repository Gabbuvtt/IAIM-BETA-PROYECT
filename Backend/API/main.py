import logging
import os
import time
import uuid
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

# Importaciones locales del proyecto IAIM
from Auth.Login import login
from . import models, schemas, database
from .database import get_db, engine
from .logging_config import configure_logging
from .routers import users, tickets

# Configura el logging estructurado (JSON) lo antes posible.
configure_logging()
logger = logging.getLogger("iaim.api")

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title="Sistema de Gestión de Tickets - IAIM",
    description="API robusta para el control de personal y mantenimiento técnico del aeropuerto."
)


# ============================================================
# MIDDLEWARE: LOG ESTRUCTURADO POR REQUEST
# ============================================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Registra cada petición HTTP en formato JSON con método, ruta, status,
    duración en ms y un request_id único (útil para correlacionar logs).
    """
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
    start = time.perf_counter()
    client_host = request.client.host if request.client else None

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.exception(
            "request failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
                "client": client_host,
            },
        )
        raise

    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["x-request-id"] = request_id

    # Health checks no merecen ruido a nivel INFO; bajan a DEBUG.
    log_method = logger.debug if request.url.path == "/health" else logger.info
    log_method(
        "request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "client": client_host,
        },
    )
    return response

# ============================================================
# CONFIGURACIÓN CORS
# ============================================================
# En producción, definir FRONTEND_URL con el dominio público de Vercel
# (puede ser una sola URL o varias separadas por coma).
# Si no se define, se permite cualquier origen (modo dev).
_frontend_url_env = os.getenv("FRONTEND_URL", "").strip()
if _frontend_url_env:
    _allowed_origins = [o.strip() for o in _frontend_url_env.split(",") if o.strip()]
    _allow_credentials = True
else:
    _allowed_origins = ["*"]
    _allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

#--- VINCULAR LAS RUTAS DE LA API ---
app.include_router(login.router)
app.include_router(users.router)
app.include_router(tickets.router)

# Sincronización automática de modelos con la base de datos (Supabase/PostgreSQL)
models.Base.metadata.create_all(bind=engine)

# ============================================================
# ENDPOINTS PRINCIPALES (ROOT)
# ============================================================

@app.get("/health")
def health_check():
    """
    Endpoint ligero de health check.
    No toca la base de datos: úsalo en Render, UptimeRobot, etc.
    """
    return {"status": "ok"}


@app.get("/api")
def api_root():
    """
    Endpoint principal de la API IAIM.
    Retorna información básica del sistema y enlaces a la documentación.
    """
    return {
        "message": "Sistema de Gestión IAIM - API",
        "version": "1.0.0",
        "description": "Sistema de gestión de tickets y personal para aeropuertos",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ============================================================
# SERVIR FRONTEND ESTÁTICO (PRODUCCIÓN)
# ============================================================
# En producción, FastAPI sirve los archivos estáticos del frontend
# generados por `vite build`. En desarrollo, Vite sirve el frontend
# desde el puerto 5000 y proxea las llamadas API a este backend.
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FRONTEND_DIST = os.path.normpath(os.path.join(_BACKEND_DIR, "..", "Frontend", "dist"))

if os.path.isdir(_FRONTEND_DIST):
    # Sirve los assets estáticos (JS, CSS, imágenes) de Vite
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(_FRONTEND_DIST, "assets")),
        name="assets",
    )

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(_FRONTEND_DIST, "index.html"))

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        """Fallback SPA: cualquier ruta no manejada devuelve index.html."""
        candidate = os.path.join(_FRONTEND_DIST, full_path)
        if os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(_FRONTEND_DIST, "index.html"))