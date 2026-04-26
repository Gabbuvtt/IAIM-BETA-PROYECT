from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..auth import role_required, get_current_user

router = APIRouter(prefix="/tickets", tags=["Gestión de Tickets"])

@router.get("/", 
        response_model=List[schemas.TicketResponse],
        dependencies=[Depends(role_required(["admin", "supervisor", "tecnico"]))])
def list_all_tickets(db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    """
    Visualiza reportes de fallas según el rol del usuario:
    
    - **admin/supervisor**: Ven todos los tickets del sistema
    - **tecnico**: Solo ve sus propios tickets asignados
    
    Retorna lista completa con información del creador y estado actual.
    """
    if current_user.rol in ["admin", "supervisor"]:
        return db.query(models.Tickets).all()
    
    return db.query(models.Tickets).filter(models.Tickets.usuario_id == str(current_user.id)).all()

@router.post("/", 
        response_model=schemas.TicketResponse, 
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(role_required(["admin", "tecnico", "supervisor"]))])
def report_new_fault(ticket: schemas.TicketCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    """
    Crea un nuevo ticket de reporte de fallas.
    
    - **asunto**: Título descriptivo del problema (5-150 caracteres)
    - **descripcion**: Detalle completo de la falla reportada
    - **prioridad**: Nivel de urgencia (baja, media, alta, critica)
    
    El usuario autenticado se asigna automáticamente como creador del ticket.
    """
    new_ticket = models.Tickets(
        **ticket.model_dump(),
        usuario_id=str(current_user.id)
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

@router.put("/{ticket_id}", 
        response_model=schemas.TicketResponse,
        dependencies=[Depends(role_required(["admin", "tecnico"]))])
def update_ticket_info(ticket_id: int, ticket_update: schemas.TicketUpdate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    """
    Actualiza completa o parcialmente un ticket (método PUT).
    
    - **ticket_id**: ID numérico del ticket a modificar
    - **prioridad**: Nuevo nivel de urgencia (opcional)
    - **estado**: Nuevo estado del ticket (abierto, en_progreso, resuelto, cerrado)
    - **descripcion**: Descripción actualizada del problema (opcional)
    
    Solo técnicos y administradores pueden modificar tickets.
    """
    db_ticket = db.query(models.Tickets).filter(models.Tickets.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado.")

    update_data = ticket_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ticket, key, value)

    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.patch("/{ticket_id}", 
        response_model=schemas.TicketResponse,
        dependencies=[Depends(role_required(["admin", "tecnico"]))])
def partial_update_ticket(ticket_id: int, ticket_update: schemas.TicketUpdate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    """
    Actualización parcial de un ticket (método PATCH).
    
    Ideal para cambios rápidos de estado o prioridad sin modificar otros campos.
    
    - **ticket_id**: ID numérico del ticket
    - Campos enviados se actualizan individualmente
    - Campos no enviados permanecen sin cambios
    """
    db_ticket = db.query(models.Tickets).filter(models.Tickets.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado.")

    update_data = ticket_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ticket, key, value)

    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.delete("/{ticket_id}", 
            dependencies=[Depends(role_required(["admin"]))])
def remove_ticket_record(ticket_id: int, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    """
    Elimina permanentemente un ticket del historial. Solo el Administrador tiene este privilegio.
    
    - **ticket_id**: ID numérico del ticket a eliminar
    - **Advertencia**: Esta acción es irreversible
    """
    db_ticket = db.query(models.Tickets).filter(models.Tickets.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Registro de falla no encontrado.")
    
    db.delete(db_ticket)
    db.commit()
    return {"status": "success", "message": f"Ticket #{ticket_id} borrado permanentemente."}
