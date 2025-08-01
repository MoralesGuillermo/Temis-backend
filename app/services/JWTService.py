import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv

import os
from datetime import datetime, timedelta, timezone

load_dotenv()

class JWTService:
    @staticmethod
    def generate_token(data: dict, expires_delta: int):
        """Generate a token for an authenticated user"""
        token_base = data.copy()
        # Set the live time of the token
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        token_base.update({"exp": expire})
        return jwt.encode(token_base, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM"))
    
    @staticmethod
    def decode(token: str) -> dict | bool:
        try:
            decoded_token =  jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM")])
            expiry = decoded_token.get("exp")
            if not expiry:
                return False
            expiry_dt = datetime.fromtimestamp(expiry, tz=timezone.utc)
            if datetime.now(timezone.utc) > expiry_dt:
                return False
            return decoded_token
        except InvalidTokenError:
            return False
                
        

            
        


    