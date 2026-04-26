from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv

# Importaciones absolutas desde la raíz del proyecto (Carpeta Backend)
from API.database import get_db
from API.models import Usuario
from API.auth import verify_password

# Cargar variables de entorno
load_dotenv()

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Configuración del Token desde variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY", "IAIM_SECRET_KEY_SUPER_SECRETA")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

def create_access_token(data: dict):
    """Genera un token JWT con tiempo de expiración."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Ruta de inicio de sesión. 
    Recibe 'username' (email) y 'password' vía Form Data.
    """
    # 1. Buscar al usuario por email
    user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    
    # 2. Verificar existencia y validar contraseña
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Crear el token con la info del usuario
    # CRÍTICO: Convertimos user.id a str() para evitar el error de JSON con UUID
    access_token = create_access_token(
        data={
            "sub": user.email, 
            "role": user.rol, 
            "user_id": str(user.id)
        }
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }