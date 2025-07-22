"""Legal case management service"""
from sqlalchemy.sql import select, exists

from app.database.database import SessionLocal
from app.database.models import User, LegalCase
from app.schemas.enums import Status

class LegalCaseService:
    @staticmethod
    def case_exists(case_id) -> bool:
        """Check if a case exists"""
        with SessionLocal() as session:
            stmt = select(exists().where(LegalCase.id == case_id))
            return session.execute(stmt).scalar() 
        
    @staticmethod
    def get_legal_case(case_id, user: User):
        """Return a legal case's data"""
        with SessionLocal() as session:
            # TODO: Add a status in legal_case_x_users to consider access management to the case.
            legal_case = session.query(LegalCase).filter(LegalCase.id == case_id, LegalCase.users.any(User.id == user.id)).first()
            return legal_case
            
    