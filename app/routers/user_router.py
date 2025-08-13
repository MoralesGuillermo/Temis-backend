
# External dependencies
from fastapi import HTTPException, status, APIRouter, Request

# Client Dependencies
from app.services.UserService import UserService
from app.services.AuthService import AuthService 
from app.schemas.UserProfileResponse import UserProfileResponse

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/profile", status_code=status.HTTP_200_OK, response_model=UserProfileResponse, description="Retorna la información completa del perfil del usuario autenticado")
def get_user_profile(request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    
    profile = UserService.get_user_profile(user)
    
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil de usuario no encontrado")
    
    return profile