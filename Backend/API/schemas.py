from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

# ==========================================
# ESQUEMAS PARA USUARIOS
# ==========================================

class UsuarioBase(BaseModel):
    """Campos compartidos para todas las operaciones de usuario"""
    nombre_completo: str = Field(..., min_length=3, max_length=100)
    carnet: str = Field(..., description="Carnet de identificación del personal")
    email: EmailStr
    rol: Optional[str] = Field(default="tecnico", pattern="^(admin|tecnico|supervisor)$")

class UsuarioCreate(UsuarioBase):
    """Esquema para el POST (Registro). Aquí recibimos la contraseña limpia."""
    password: str = Field(..., min_length=8)

class UsuarioUpdate(BaseModel):
    """Esquema para el PUT/PATCH. Todo es opcional para permitir cambios parciales."""
    nombre_completo: Optional[str] = None
    email: Optional[EmailStr] = None
    rol: Optional[str] = None
    # No permitimos cambiar el carnet ni el ID por aquí

class UsuarioResponse(UsuarioBase):
    """Esquema para el GET. Lo que enviamos al frontend (Sin contraseña)."""
    id: UUID

    class Config:
        # Esto es vital para que Pydantic entienda los modelos de SQLAlchemy
        from_attributes = True


# ==========================================
# ESQUEMAS PARA TICKETS
# ==========================================

class TicketBase(BaseModel):
    """Campos base para la gestión de reportes del aeropuerto"""
    asunto: str = Field(..., min_length=5, max_length=150)
    descripcion: str
    prioridad: Optional[str] = Field(default="media", pattern="^(baja|media|alta|critica)$")

class TicketCreate(TicketBase):
    """Esquema para el POST. Ya no pedimos usuario_id aquí porque lo tomamos del Token."""
    pass

class TicketUpdate(BaseModel):
    """Esquema para el PUT. Para cambiar el estado o la prioridad."""
    prioridad: Optional[str] = None
    estado: Optional[str] = Field(None, pattern="^(abierto|en_progreso|resuelto|cerrado)$")
    descripcion: Optional[str] = None

class TicketResponse(TicketBase):
    """Esquema para el GET. Información completa del ticket."""
    id: int
    estado: str
    usuario_id: UUID
    fecha_creacion: datetime

    class Config:
        from_attributes = True