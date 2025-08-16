# app/routers/agenda_router.py
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Request, Query

from app.services.AuthService import AuthService
from app.services.AgendaService import AgendaService
from app.schemas.Agenda import AgendaCreate, AgendaOut, AgendaUpdate, FirstMeetingIn

UNAUTHORIZED_MSG = "Usuario no autenticado. Debe iniciar sesión para poder visualizar este recurso."

router = APIRouter(prefix="/agenda", tags=["agenda"])

def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    # Espera ISO-8601 con TZ: 2025-08-13T09:00:00-06:00
    return datetime.fromisoformat(value)

@router.post("/new", status_code=status.HTTP_200_OK, response_model=AgendaOut,
             description="Crea un nuevo evento en la agenda del usuario autenticado")
def create_event(payload: AgendaCreate, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_MSG)

    created = AgendaService.create_event(payload, user)
    if not created:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo crear el evento.")
    return created

@router.get("/items/all", status_code=status.HTTP_200_OK, response_model=List[AgendaOut],
            description="Obtiene todos los eventos de la agenda del usuario (con filtros)")
def list_all_items(
    request: Request,
    date_from: Optional[str] = Query(None, description="ISO-8601 con TZ"),
    date_to: Optional[str] = Query(None, description="ISO-8601 con TZ"),
    q: Optional[str] = Query(None, description="Texto en título/descripcion"),
    tags: Optional[List[str]] = Query(None, description="Debe contener todos los tags indicados"),
):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_MSG)

    return AgendaService.get_all(
        user=user,
        date_from=_parse_dt(date_from),
        date_to=_parse_dt(date_to),
        q=q,
        tags=tags,
    )


@router.put("/update/{agenda_id}", status_code=status.HTTP_200_OK, response_model=AgendaOut,
            description="Actualiza un evento de la agenda del usuario autenticado")
def update_event(agenda_id: int, payload: AgendaUpdate, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_MSG)

    updated = AgendaService.update_event(agenda_id=agenda_id, data=payload, user=user)
    if not updated:
        # no existe o no pertenece al usuario
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el evento o no tiene permisos.")
    return updated


@router.delete("/delete/{agenda_id}", status_code=status.HTTP_200_OK,
               description="Elimina un evento de la agenda del usuario autenticado")
def delete_event(agenda_id: int, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_MSG)

    ok = AgendaService.delete_event(agenda_id=agenda_id, user=user)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el evento o no tiene permisos.")
    return {"deleted": True, "id": agenda_id}



@router.post("/{case_id}/first-meeting", status_code=status.HTTP_201_CREATED, response_model=AgendaOut,
             description="Crea la primera reunión del caso (título/descripcion automáticos)")
def create_first_meeting(case_id: int, payload: FirstMeetingIn, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_MSG)

    return AgendaService.create_first_meeting(
    case_id=case_id, meeting_date=payload.meeting_date, user=user
)
