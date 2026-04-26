import bcrypt
from . import models
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from .database import get_db

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de seguridad desde variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY", "IAIM_SECRET_KEY_SUPER_SECRETA")
ALGORITHM = "HS256"

# Define el esquema de donde FastAPI sacará el token (del header Authorization: Bearer ...)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ============================================================
# FUNCIONES DE SEGURIDAD (PASSWORD HASHING)
# ============================================================

def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro para la contraseña usando el algoritmo bcrypt.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con el hash almacenado.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# ============================================================
# AUTENTICACIÓN Y CONTROL DE ACCESO (RBAC)
# ============================================================

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Dependencia que identifica al usuario actual descifrando el Token JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token de acceso",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 2. Buscar al usuario en la base de datos por el email extraído del token
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuario del token no encontrado"
        )
    return user

def role_required(allowed_roles: list[str]):
    """
    Fábrica de dependencias que valida si el usuario tiene el rol permitido.
    Recibe una lista de roles y verifica al usuario obtenido del token.
    """
    def role_checker(current_user: models.Usuario = Depends(get_current_user)):
        if current_user.rol not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permisos insuficientes. Requiere: {allowed_roles}"
            )
        return current_user
    return role_checker