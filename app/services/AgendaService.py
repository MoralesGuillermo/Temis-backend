# app/services/AgendaService.py
from typing import Optional, List
from datetime import datetime

from app.database.database import SessionLocal
from app.database.models import Agenda, User
from app.schemas.Agenda import AgendaOut, AgendaCreate , AgendaUpdate

class AgendaService:
    @staticmethod
    def create_event(data: AgendaCreate, user: "User") -> AgendaOut | bool:
        """Crea un evento en la agenda del usuario."""
        with SessionLocal() as session:
            item = Agenda(
                event_name=data.event_name,
                description=data.description,
                due_date=data.due_date,
                tags=data.tags or [],
                account_id=user.account_id,
                user_id=user.id,
            )
            session.add(item)
            session.commit()
            session.refresh(item)
            return AgendaOut.model_validate(item)

    @staticmethod
    def _apply_filters(query, date_from: Optional[datetime], date_to: Optional[datetime],
                       q: Optional[str], tags: Optional[List[str]]):
        if date_from:
            query = query.filter(Agenda.due_date >= date_from)
        if date_to:
            query = query.filter(Agenda.due_date <= date_to)
        if q:
            like = f"%{q}%"
            # PostgreSQL ILIKE for case-insensitive search
            # Search in both event_name and description
            query = query.filter(
                (Agenda.event_name.ilike(like)) | (Agenda.description.ilike(like))
            )
        if tags:
            # PostgreSQL ARRAY: contiene TODOS los tags indicados
            query = query.filter(Agenda.tags.contains(tags))
        return query

    @staticmethod
    def get_all(user: "User",
                date_from: Optional[datetime],
                date_to: Optional[datetime],
                q: Optional[str],
                tags: Optional[List[str]]) -> List[AgendaOut]:
        """Lista todos los eventos del usuario (con filtros)."""
        with SessionLocal() as session:
            query = session.query(Agenda).filter(
                Agenda.user_id == user.id,
                Agenda.account_id == user.account_id,
            )
            query = AgendaService._apply_filters(query, date_from, date_to, q, tags)
            items = query.order_by(Agenda.due_date.asc(), Agenda.id.asc()).all()
            return [AgendaOut.model_validate(x) for x in items]
        
    @staticmethod
    def update_event(agenda_id: int, data: AgendaUpdate, user: "User") -> AgendaOut | bool:
        """
        Actualiza un evento del usuario.
        Solo permite actualizar eventos que pertenezcan al user (user_id/account_id).
        """
        with SessionLocal() as session:
            item = session.query(Agenda).filter(
                Agenda.id == agenda_id,
                Agenda.user_id == user.id,
                Agenda.account_id == user.account_id,
            ).first()
            if not item:
                return False

            # Solo actualizar campos presentes (partial update)
            update_dict = data.model_dump(exclude_unset=True)
            if "event_name" in update_dict:
                item.event_name = update_dict["event_name"]
            if "description" in update_dict:
                item.description = update_dict["description"]
            if "due_date" in update_dict:
                item.due_date = update_dict["due_date"]
            if "tags" in update_dict:
                # Nota: reemplaza completamente las tags si envías la lista
                item.tags = update_dict["tags"] if update_dict["tags"] is not None else item.tags

            session.commit()
            session.refresh(item)
            return AgendaOut.model_validate(item)

    @staticmethod
    def delete_event(agenda_id: int, user: "User") -> bool:
        """
        Elimina un evento del usuario.
        """
        with SessionLocal() as session:
            item = session.query(Agenda).filter(
                Agenda.id == agenda_id,
                Agenda.user_id == user.id,
                Agenda.account_id == user.account_id,
            ).first()
            if not item:
                return False
            session.delete(item)
            session.commit()
            return True

 
            return [AgendaOut.model_validate(x) for x in items]
