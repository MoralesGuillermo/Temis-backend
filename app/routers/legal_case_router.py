
# External dependencies
from fastapi import HTTPException, status, Response, APIRouter, Request

# Client Dependencies
from app.services.LegalCaseService import LegalCaseService
from app.services.AuthService import AuthService 

router = APIRouter(prefix="/legal", tags=["legal case"])


@router.get("/get", status_code=status.HTTP_200_OK, description="Retorna los datos de un caso si el usuario esta autorizado a verlo")
def get_legal_case(case_id: int, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado. Debe inicar sesión para poder visualizar este recurso.")
    if not LegalCaseService.case_exists(case_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el caso seleccionado.")
    case = LegalCaseService.get_legal_case(case_id, user)
    # Case is not found if the user is not assigned to it
    if not case:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No cuenta con los permisos para acceder a este caso.")
    # TODO: Make schema for LegalCase return type
    return case



