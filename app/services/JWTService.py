import jwt
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
                
        

            
        


    