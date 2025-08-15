# In-built dependencies
from typing import Annotated
import os

# External dependencies
from fastapi import Depends, HTTPException, status, Response, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

# Client Dependencies
from app.services.AuthService import AuthService
from app.services.utils.hash.HashCrypt import HashCrypt
from app.services.JWTService import JWTService
from app.schemas.UserResponse import UserResponse
from app.schemas.RegisterRequest import RegisterRequest, RegisterResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK, response_model=UserResponse, description="Inicio de sesión con generación de JWT")
def authenticate(credentials: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response):
    auth = AuthService(HashCrypt())
    user = auth.login(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    token_expiry = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    jwt_token = JWTService.generate_token(data={"sub": str(user)}, expires_delta=token_expiry)
    # TODO: Get HTTPS certificate on site to send credentials to frontend. After that, activate secure=True. Get domain so samesite can be lax
    # Return a partitioned cookie
    response.headers["Set-Cookie"] = f'accessToken={jwt_token}; HttpOnly; SameSite=None; Secure; Path=/; Partitioned;'
    return user

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=RegisterResponse, description="Registro de nuevo usuario")
def register(payload: RegisterRequest):
    auth = AuthService(HashCrypt())
    user = auth.register(payload)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo crear el usuario. Verifique los datos proporcionados")
    return user