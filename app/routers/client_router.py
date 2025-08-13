
# External dependencies
from fastapi import HTTPException, status, Response, APIRouter, Request

# Client Dependencies
from app.services.LegalCaseService import ClientService
from app.services.AuthService import AuthService 
from app.schemas.LegalCaseNotesUpdate import LegalCaseNotesUpdate
from app.schemas.ClientOut import ClientOut


router = APIRouter(prefix="/client", tags=["Client"])


@router.get("/get", status_code=status.HTTP_200_OK, response_model=ClientOut, description="Retorna los datos de datos de un cliente si este se encuentra en el sistema")
def get_client_by_dni(client_dni: str, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado. Debe inicar sesión para poder visualizar este recurso.")
    client = ClientService.get_client_by_dni(client_dni, user)
    # Case is not found if the user is not assigned to it
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el cliente solicitado")
    return client







