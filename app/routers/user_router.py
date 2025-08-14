
# External dependencies
from fastapi import HTTPException, status, APIRouter, Request

# Client Dependencies
from app.services.UserService import UserService
from app.services.AuthService import AuthService 
from app.schemas.UserProfileResponse import UserProfileResponse
from app.schemas.EditProfileRequest import EditProfileRequest, EditProfileResponse, ChangePasswordRequest, ChangePasswordResponse
from app.schemas.RegisterUserRequest import RegisterUserRequest, RegisterUserResponse

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

@router.put("/profile", status_code=status.HTTP_200_OK, response_model=EditProfileResponse, description="Actualiza la información del perfil del usuario autenticado")
def edit_user_profile(payload: EditProfileRequest, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    
    response = UserService.edit_profile(payload, user)
    return response

@router.put("/change-password", status_code=status.HTTP_200_OK, response_model=ChangePasswordResponse, description="Cambia la contraseña del usuario autenticado")
def change_user_password(payload: ChangePasswordRequest, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    
    response = UserService.change_password(payload, user)
    return response

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=RegisterUserResponse, description="Registra un nuevo usuario en la cuenta del usuario autenticado")
def register_user(payload: RegisterUserRequest, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    
    response = UserService.register_user(payload, user)
    return response