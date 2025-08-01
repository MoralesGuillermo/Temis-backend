# Client Dependencies
"""App authenticatino and authorization service"""
from app.services.utils.hash.Hash import Hash
from app.database.database import SessionLocal
from app.database.models import User
from app.schemas.enums import Status
from app.services.JWTService import JWTService



class AuthService:
    def __init__(self, hash_service: Hash):
        self.hash_service = hash_service
    
    def login(self, username, password) -> bool:
        """Check if a user has the correct credentials to login"""
        with SessionLocal() as session:
            user = session.query(User).filter(User.username == username, User.status == Status.ACTIVE).first()
            if not user:
                return False
            if not self.hash_service.verify(password, user.password):
                return False
            return user
        
    @staticmethod
    def get_active_user(token: str) -> User | bool:
        decoded_token = JWTService.decode(token)
        if not decoded_token:
            return False
        user_id = decoded_token.get("sub")
        if not user_id:
            return False
        with SessionLocal() as session:
            return session.query(User).filter(User.id == user_id).first()
        
            
        


    