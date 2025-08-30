"""App's auth middleware"""
from fastapi import Request, HTTPException, status



from app.services.AuthService import AuthService
from app.services.utils.hash.HashCrypt import HashCrypt

def is_authenticated(request: Request, call_next: function):
    """Check if a request is authenticated"""
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado. Debe autenticarse para actualizar este recurso.")
    request.state.user = user
    return call_next(request)
    

    