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

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK, response_model=UserResponse, description="Inicio de sesión con generación de JWT")
def authenticate(credentials: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response):
    auth = AuthService(HashCrypt())
    user = auth.login(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    token_expiry = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    jwt_token = JWTService.generate_token(data={"sub": str(user)}, expires_delta=token_expiry)
    # TODO: Get HTTPS certificate on site to send credentials to frontend. After that, activate secure=True
    response.set_cookie(key="accessToken", value=jwt_token, httponly=True, secure=True, samesite="none")
    return user