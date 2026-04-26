from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

# Importaciones locales del proyecto IAIM
from Auth.Login import login
from . import models, schemas, database
from .database import get_db, engine
from .routers import users, tickets

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title="Sistema de Gestión de Tickets - IAIM",
    description="API robusta para el control de personal y mantenimiento técnico del aeropuerto."
)

# Configuración CORS para permitir comunicación con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
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

@app.get("/")
def root():
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