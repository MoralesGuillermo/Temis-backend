"""Legal case management service"""
from sqlalchemy.sql import select, exists

from app.database.database import SessionLocal
from app.database.models import User, LegalCase
from app.schemas.LegalCaseOut import LegalCaseOut

class LegalCaseService:
    @staticmethod
    def case_exists(case_id) -> bool:
        """Check if a case exists"""
        with SessionLocal() as session:
            stmt = select(exists().where(LegalCase.id == case_id))
            return session.execute(stmt).scalar() 
        
    @staticmethod
    def get_legal_case(case_id, user: User) -> LegalCase:
        """Return a legal case's data"""
        with SessionLocal() as session:
            legal_case = LegalCaseService._fetch_case(case_id, user, session)
            return legal_case
        
    @staticmethod
    def update_notes(case_id: int, notes: str, user: User) -> LegalCase | bool:
        """Update the notes in a legal case"""
        with SessionLocal() as session:
            legal_case = LegalCaseService._fetch_case(case_id, user, session)
            if not legal_case:
                # The user doesn't have the permission to access the legal case
                return False
            legal_case.notes = notes
            session.commit()
            return LegalCaseOut.from_orm(legal_case)
        
    @staticmethod
    def _fetch_case(case_id, user: User, session):
        """Fetch a case injecting a session"""
        # TODO: Add a status in legal_case_x_users to consider access management to the case.
        return session.query(LegalCase).filter(LegalCase.id == case_id, LegalCase.users.any(User.id == user.id)).first()
            
    