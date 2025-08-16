# app/services/AgendaService.py
from typing import Optional, List
from datetime import datetime, time, timezone
from sqlalchemy import select
from fastapi import HTTPException, status

from app.database.database import SessionLocal
from app.database.models import Agenda, User, LegalCase
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

    @staticmethod
    def create_first_meeting(case_id: int, meeting_date, user: "User") -> AgendaOut:
        """
        Crea la 'Primera reunión' de un caso, generando título/descripcion y tags.
        Evita duplicados por (case_id, first_meeting).
        """
        with SessionLocal() as session:
            case = session.get(LegalCase, case_id)
            if not case:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

            # Verifica pertenencia a la misma cuenta (ajusta si usas otro control de acceso)
            if case.account_id != user.account_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this case")

            # Idempotencia: si ya existe un first_meeting para este caso, devolverlo
            existing = session.execute(
                select(Agenda).where(
                    Agenda.account_id == user.account_id,
                    Agenda.user_id == user.id,  # si quieres que sea por usuario, déjalo; si debe ser por cuenta, quita esta línea
                    Agenda.tags.contains(["first_meeting", f"case:{case_id}"])
                )
            ).scalars().first()
            if existing:
                return AgendaOut.model_validate(existing)

            # Construir título y descripción
            title = f"Primera reunión – {case.title}"
            desc = f"Reunión inicial del caso '{case.title}'."
            if case.description:
                desc += f" {case.description[:200]}"

            # Convertir date -> datetime a las 09:00 (UTC) para due_date
            start_dt = datetime.combine(meeting_date, time(9, 0)).replace(tzinfo=timezone.utc)

            payload = AgendaCreate(
                event_name=title,
                description=desc,
                due_date=start_dt,
                tags=["case", f"case:{case_id}", "first_meeting"]
            )

            # Crea mediante tu servicio existente
            from app.services.AgendaService import AgendaService
            created = AgendaService.create_event(payload, user)
            return created 