from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..auth import get_password_hash, role_required, get_current_user

router = APIRouter(prefix="/users", tags=["Gestión de Usuarios"])

@router.get("/me", response_model=schemas.UsuarioResponse)
def get_current_user_info(current_user: models.Usuario = Depends(get_current_user)):
    """
    Obtiene la información del usuario actualmente autenticado.
    
    - Requiere token JWT válido en el header Authorization
    - Retorna datos del usuario sin la contraseña
    """
    return current_user

@router.get("/", 
        response_model=List[schemas.UsuarioResponse],
        dependencies=[Depends(role_required(["admin", "supervisor"]))])
def get_all_users(db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    """
    Obtiene la lista completa de empleados. Solo para nivel administrativo.
    
    - **admin**: Acceso completo a todos los usuarios
    - **supervisor**: Acceso de solo lectura a todos los usuarios
    """
    return db.query(models.Usuario).all()

@router.post("/", 
        response_model=schemas.UsuarioResponse, 
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(role_required(["admin"]))])
def create_new_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    """
    Registra un nuevo usuario en el sistema. Solo el Administrador puede realizar esta acción.
    
    - **nombre_completo**: Nombre completo del empleado (3-100 caracteres)
    - **carnet**: Número de identificación único del personal
    - **email**: Correo electrónico corporativo (único)
    - **password**: Contraseña mínima de 8 caracteres
    - **rol**: Rol del usuario (admin, tecnico, supervisor)
    """
    if db.query(models.Usuario).filter(models.Usuario.email == user.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado.")

    new_user = models.Usuario(
        nombre_completo=user.nombre_completo,
        carnet=user.carnet,
        email=user.email,
        password_hash=get_password_hash(user.password),
        rol=user.rol
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/{user_id}", 
        response_model=schemas.UsuarioResponse,
        dependencies=[Depends(role_required(["admin"]))])
def update_existing_user(user_id: str, user_update: schemas.UsuarioCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    """
    Modifica datos completos de un usuario existente. Solo el Administrador puede realizar esta acción.
    
    - **user_id**: UUID del usuario a modificar
    - Todos los campos son requeridos para la actualización completa
    """
    db_user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    db_user.nombre_completo = user_update.nombre_completo
    db_user.carnet = user_update.carnet
    db_user.email = user_update.email
    db_user.rol = user_update.rol
    
    if user_update.password:
        db_user.password_hash = get_password_hash(user_update.password)

    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", 
            dependencies=[Depends(role_required(["admin"]))])
def delete_user_account(user_id: str, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    """
    Elimina permanentemente un usuario del sistema. Solo para el Administrador.
    
    - **user_id**: UUID del usuario a eliminar
    - **Advertencia**: Esta acción es irreversible y eliminará todos los tickets asociados
    """
    db_user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no existe.")
    
    db.delete(db_user)
    db.commit()
    return {"status": "success", "message": "Usuario eliminado correctamente."}

@router.post("/link-telegram")
def link_telegram_account(
    email: str,
    telegram_chat_id: str,
    db: Session = Depends(get_db)
):
    """
    Vincula una cuenta de Telegram con un usuario existente.
    
    - **email**: Email del usuario a vincular
    - **telegram_chat_id**: Chat ID de Telegram del usuario
    """
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado con ese email")
    
    user.telegram_chat_id = telegram_chat_id
    db.commit()
    db.refresh(user)
    
    return {"status": "success", "message": f"Usuario {user.nombre_completo} vinculado a Telegram"}
