import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship # <--- Nueva importación para las relaciones
from .database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    nombre_completo = Column(String, nullable=False)
    carnet = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(String, nullable=False) # admin, tecnico, supervisor
    telegram_chat_id = Column(String, nullable=True) # Para autenticación por Telegram

    # RELACIÓN: Un usuario puede tener muchos tickets asignados
    tickets = relationship("Tickets", back_populates="creador")

class Tickets(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    asunto = Column(String, nullable=False)
    descripcion = Column(Text, nullable=False)
    prioridad = Column(String, default="media") # alta, media, baja
    estado = Column(String, default="abierto") # abierto, en proceso, cerrado
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)

    # LLAVE FORÁNEA: Columna física que guarda el ID del usuario
    usuario_id = Column(String, ForeignKey("usuarios.id"))

    # RELACIÓN: Un ticket pertenece a un creador (Usuario)
    creador = relationship("Usuario", back_populates="tickets")