from typing import Annotated, List, Optional

# External dependencies
from fastapi import HTTPException, status, Response, APIRouter, Request, UploadFile, File
from fastapi.responses import StreamingResponse

# Client Dependencies
from app.services.LegalCaseService import LegalCaseService
from app.services.AuthService import AuthService 
from app.schemas.LegalCaseNotesUpdate import LegalCaseNotesUpdate
from app.schemas.LegalCaseOut import LegalCaseOut
from app.schemas.FileOut import FileOut
from app.schemas.NewCaseData import NewCaseData
from app.services.utils.storage.AWSStorage import AWSStorage

# Blob storage
STORAGE = AWSStorage()

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


# Endpoint para obtener todos los casos del usuario
@router.get("/cases", status_code=status.HTTP_200_OK, description="Obtiene todos los casos del usuario autenticado")
def get_all_user_cases(request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_MSG)
    
    # Obtener todos los casos del usuario
    cases = LegalCaseService.get_all_cases(user)
    return cases

# Endpoint para obtener métricas de casos del usuario
@router.get("/cases/metrics", status_code=status.HTTP_200_OK, description="Obtiene las métricas de casos del usuario")
def get_cases_metrics(request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado.")
    
    # Obtener métricas de casos del usuario
    metrics = LegalCaseService.get_cases_metrics(user)
    return metrics

# Endpoint para actualizar un caso completo (no solo las notas)
@router.put("/cases/{case_id}", status_code=status.HTTP_200_OK, response_model=LegalCaseOut, description="Actualiza un caso completo")
async def update_case(case_id: int, case_update: dict, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_MSG)
    
    if not LegalCaseService.case_exists(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el caso peticionado.")
    
    updated_case = LegalCaseService.update_case(case_id, case_update, user)
    if not updated_case:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No cuenta con los permisos para actualizar este caso.")
    
    return updated_case

@router.get("/files/all", status_code=status.HTTP_200_OK, response_model=List[FileOut], description="Retorna los datos de los archivos de un caso (No retorna los archivos como tal)")
async def get_case_files(case_id: int, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado. Debe autenticarse para actualizar este recurso.")
    if not LegalCaseService.case_exists(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_MSG)
    files = LegalCaseService.get_all_files(case_id, user)
    if not files:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No cuenta con los permisos para ver los archivos de este caso")
    return files

@router.get("/files/{page}", status_code=status.HTTP_200_OK, response_model=List[FileOut], description="Retorna los datos de los archivos de un caso (No retorna los archivos como tal)")
async def get_case_files_by_page(case_id: int, request: Request, page: int=0, page_size: int=10):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado. Debe autenticarse para actualizar este recurso.")
    if not LegalCaseService.case_exists(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_MSG)
    files = LegalCaseService.get_files_by_page(case_id, user, page, page_size)
    if files == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No cuenta con los permisos para ver los archivos de este caso")
    if len(files) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró la página de archivos solicitada")
    return files

@router.get("/files/get/amount", status_code=status.HTTP_200_OK, description="Retorna la cantidad de archivos que tiene un caso")
async def get_case_file_amount(case_id: int, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado. Debe autenticarse para actualizar este recurso.")
    if not LegalCaseService.case_exists(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_MSG)
    file_amount = LegalCaseService.file_amount(case_id, user)
    if not file_amount:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No cuenta con los permisos para ver los archivos de este caso")
    return {"amount": file_amount}


@router.post("/file/upload", status_code=status.HTTP_200_OK, response_model=FileOut, description="Guarda y sube un archivo en la DB y el Blob Storage")
async def upload_file(case_id: int,  request: Request, file: UploadFile = File(...)):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado. Debe autenticarse para actualizar este recurso.")
    if not LegalCaseService.case_exists(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_MSG)
    if not LegalCaseService.authorized_user(case_id, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=UNAUTHORIZED_MSG)
    if not LegalCaseService.has_available_storage(case_id, file):
        raise HTTPException(status_code=status.HTTP_507_INSUFFICIENT_STORAGE, 
                            detail="No cuenta con la cantidad suficiente de almacenamiento. Puede mejorar su plan de almacenamiento de Temis Software!"
        )
    if LegalCaseService.file_exists(case_id, file):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Un archivo con ese nombre ya existe en este caso.")
    # Name used in the blob storage
    print(file.filename)
    object_name = f"{case_id}/{file.filename}"
    file_was_uploaded = LegalCaseService.upload_file_to_storage(object_name,  file, STORAGE)
    if not file_was_uploaded:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No se pudo guardar el archivo en la nube. Favor intente mas tarde.")
    saved_file = LegalCaseService.save_file(case_id, user, file)
    return saved_file


@router.get("/file/get", status_code=status.HTTP_200_OK, description="Consigue un archivo desde el Blob Storage")
async def get_file(case_id: int, file_id, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado. Debe autenticarse para actualizar este recurso.")
    if not LegalCaseService.case_exists(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_MSG)
    if not LegalCaseService.authorized_user(case_id, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=UNAUTHORIZED_MSG)
    file_stream, content_type = LegalCaseService.get_file(file_id, STORAGE)
    if not file_stream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el archivo")
    return StreamingResponse(file_stream, media_type=content_type)
        



