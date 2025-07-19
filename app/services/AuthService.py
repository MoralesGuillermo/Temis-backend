from sqlalchemy import select

# Client Dependencies
from app.services.utils.hash.Hash import Hash
from app.services.utils.hash.HashCrypt import HashCrypt
from app.database.database import SessionLocal
from app.database.models import User



class AuthService:
    def __init__(self, hash_service: Hash):
        self.hash_service = hash_service
    
    def login(self, username, password) -> bool:
        """Check if a user has the correct credentials to login"""
        with SessionLocal() as session:
            user = session.query(User).filter(User.username == username).first()
            if not user:
                return False
            if not self.hash_service.verify(password, user.password):
                return False
            return user
            
        


    