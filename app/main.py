# In-built dependencies
from typing import Union
from typing import Annotated
import os

# External dependencies
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Client Dependencies
from app.services.AuthService import AuthService
from app.services.utils.hash.HashCrypt import HashCrypt
from app.services.JWTService import JWTService

load_dotenv()
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/login")
def authenticate(credentials: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response):
    auth = AuthService(HashCrypt())
    user = auth.login(credentials.username, credentials.password)
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    token_expiry = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    jwt_token = JWTService.generate_token(data={"sub": user}, expires_delta=token_expiry)
    response.set_cookie(key="accessToken", value=jwt_token, httponly=True, secure=True, samesite="strict")
    # TODO: Create user response model so user sensitive data is not exposed to the frontend
    return user
            


