"""Legal case management service"""
from sqlalchemy.sql import select, exists

from app.database.database import SessionLocal
from app.database.models import User, LegalCase, File
from app.schemas.LegalCaseOut import LegalCaseOut
from app.schemas.NewCaseData import NewCaseData
from app.services.ClientService import ClientService

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
    def new_case(data: NewCaseData, user:User, files):
        """Create a new case in a law firm"""
        with SessionLocal() as session:
            client = ClientService.get_client(data.client_id, session) if data.client_id else ClientService.new_client(data.client)
            new_client = session.add(client)
            case = LegalCase(
                title=data.title, 
                start_date=data.start_date,
                case_type=data.case_type,
                plaintiff=data.plaintiff,
                defendant=data.defendant,
                description=data.description,
                notes=data.notes,
                client=new_client,
                account=user.account
            )
            new_case = session.add(case)
            session.commit()
            return new_case
        
    @staticmethod
    def get_all_files(case_id: int, user: User) -> list[File] | bool:
        """Retrieve all the files' data of a case"""
        with SessionLocal() as session:
            legal_case = LegalCaseService._fetch_case(case_id, user, session)
            if not legal_case:
                # The user doesn't have the permission to access the legal case
                return False
            return legal_case.files
        
    @staticmethod
    def get_files_by_page(case_id: int, user: User, page: int=0, page_size: int=10) -> list[File] | bool:
        """Retrieve all the files' data of a case"""
        low_limit = page_size * page
        upper_limit = low_limit + page_size
        with SessionLocal() as session:
            legal_case = LegalCaseService._fetch_case(case_id, user, session)
            if not legal_case:
                # The user doesn't have the permission to access the legal case
                return False
            if len(legal_case.files) < low_limit:
                # The requested page doesn't exist
                return []
            if len(legal_case.files) <= upper_limit:
                # Send only the last remaining pages
                upper_limit = -1
            files = list(legal_case.files)
            return files[low_limit: upper_limit]
            
        
    @staticmethod
    def file_amount(case_id: int, user: User) -> int:
        """Return the amount of files in a case"""
        with SessionLocal() as session:
            legal_case = LegalCaseService._fetch_case(case_id, user, session)
            if not legal_case:
                # The user doesn't have the permission to access the legal case
                return False
            return len(legal_case.files)

    @staticmethod
    def upload_file(file, case):
        """Upload a file to a case"""
        pass
            
    @staticmethod
    def _fetch_case(case_id, user: User, session):
        """Fetch a case injecting a session"""
        # TODO: Add a status in legal_case_x_users to consider access management to the case.
        return session.query(LegalCase).filter(LegalCase.id == case_id, LegalCase.users.any(User.id == user.id)).first()