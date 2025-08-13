from typing import Annotated, List, Optional

# External dependencies
from fastapi import HTTPException, status, Response, APIRouter, Request, UploadFile, Form

# Client Dependencies
from app.services.LegalCaseService import LegalCaseService
from app.services.AuthService import AuthService 
from app.schemas.LegalCaseNotesUpdate import LegalCaseNotesUpdate
from app.schemas.LegalCaseOut import LegalCaseOut
from app.schemas.NewCaseData import NewCaseData


# Message Constants
UNAUTHORIZED_MSG = "Usuario no autenticado. Debe inicar sesión para poder visualizar este recurso."
NOT_FOUND_MSG = "No se encontró el caso peticionado."


router = APIRouter(prefix="/legal", tags=["legal case"])


@router.get("/get", status_code=status.HTTP_200_OK, response_model=LegalCaseOut, description="Retorna los datos de un caso si el usuario está autorizado a verlo")
def get_legal_case(case_id: int, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_MSG)
    if not LegalCaseService.case_exists(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_MSG)
    case = LegalCaseService.get_legal_case(case_id, user)
    # Case is not found if the user is not assigned to it
    if not case:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No cuenta con los permisos para acceder a este caso.")
    return case


@router.post("/new", status_code=status.HTTP_200_OK, response_model=LegalCaseOut, description="Crea un nuevo caso, asignando cliente, notas y guardando archivos")
def new_case(new_case_data: NewCaseData, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_MSG)
    if not new_case_data.client_id and not new_case_data.client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se recibió un cliente para asignarlo al caso")
    new_case = LegalCaseService.new_case(new_case_data, user)
    if not new_case:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo crear el caso. Porfavor vuelva a intentarlo y verifique los datos")
    return new_case


@router.post("/upload", status_code=status.HTTP_200_OK, response_model=LegalCaseOut, description="Sube un archivo a un caso")
def new_case(case_id: int, file: UploadFile, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_MSG)
    if not LegalCaseService.case_exists(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_MSG)
    # TODO: Make logic to upload file to Storage service and assign its url to the legal case
    pass


@router.put("/update/notes", status_code=status.HTTP_200_OK, response_model=LegalCaseOut, description="Actualiza las notas de un caso legal si el usuario tiene los permisos")
async def update_legal_case_notes(case_update: LegalCaseNotesUpdate, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado. Debe autenticarse para actualizar este recurso.")
    if not LegalCaseService.case_exists(case_update.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_MSG)
    updated_case = LegalCaseService.update_notes(case_update.id, case_update.notes, user)
    if not updated_case:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No cuenta con los permisos para actualizar las notas este caso.")
    return updated_case






