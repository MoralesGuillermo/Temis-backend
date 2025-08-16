"""Legal case management service"""
from sqlalchemy.sql import select, exists
from fastapi import UploadFile

# In-built dependencies
from datetime import datetime


from app.database.database import SessionLocal
from app.database.models import User, LegalCase, File
from app.schemas.LegalCaseOut import LegalCaseOut
from app.schemas.FileOut import FileOut
from app.schemas.NewCaseData import NewCaseData
from app.services.ClientService import ClientService
from app.services.utils.storage.Storage import Storage
from app.database.enums import StatusEnum

class LegalCaseService:
    @staticmethod
    def case_exists(case_id) -> bool:
        """Check if a case exists"""
        with SessionLocal() as session:
            stmt = select(exists().where(LegalCase.id == case_id))
            return session.execute(stmt).scalar()
        
    @staticmethod
    def authorized_user(case_id: int, user: User) -> bool:
        """Check if a user is authorized to interact with a case"""
        with SessionLocal() as session:
            return True if LegalCaseService._fetch_case(case_id, user, session) else False
    
    @staticmethod
    def get_legal_case(case_id, user: User) -> LegalCase:
        """Return a legal case's data"""
        with SessionLocal() as session:
            legal_case = LegalCaseService._fetch_case(case_id, user, session)
            if not legal_case:
                return False
            return LegalCaseOut.model_validate(legal_case)
        
    @staticmethod
    def update_notes(case_id: int, notes: str, user: User) -> LegalCaseOut | bool:
        """Update the notes in a legal case"""
        with SessionLocal() as session:
            legal_case = LegalCaseService._fetch_case(case_id, user, session)
            if not legal_case:
                # The user doesn't have the permission to access the legal case
                return False
            legal_case.notes = notes
            session.commit()
            return LegalCaseOut.model_validate(legal_case)
        
    @staticmethod
    def new_case(data: NewCaseData, user: User, files=None):
        """Create a new case in a law firm"""
        with SessionLocal() as session:
            # Obtener o crear cliente
            if data.client_id:
                client = ClientService.get_client(data.client_id, session)
            else:
                client = ClientService.new_client(data.client)
        
        session.add(client)
        session.flush()  # Para obtener el ID del cliente
        
        # OBTENER EL USUARIO EN LA SESIÓN ACTUAL
        current_user = session.get(User, user.id)
        if not current_user:
            raise ValueError("Usuario no encontrado")
        
        # Crear el caso usando account_id directamente
        case = LegalCase(
            title=data.title,
            start_date=data.start_date,
            case_type=data.case_type,
            description=data.description,
            notes=data.notes or '',
            client=client,
            account_id=user.account_id
        )
        
        session.add(case)
        session.flush()  # Para obtener el ID del caso
        
        case.users.add(current_user)
        
        session.commit()
        session.refresh(case)
        
        return LegalCaseOut.model_validate(case)
    
    @staticmethod
    def get_all_cases(user: User):
        """Obtiene todos los casos del usuario"""
        with SessionLocal() as session:
            cases = session.query(LegalCase).filter(
                LegalCase.users.any(User.id == user.id)
            ).all()
            return [LegalCaseOut.model_validate(case) for case in cases]

    @staticmethod
    def get_cases_metrics(user: User):
        """Obtiene las métricas de casos del usuario"""
        with SessionLocal() as session:
            # Obtener todos los casos del usuario
            cases = session.query(LegalCase).filter(
                LegalCase.users.any(User.id == user.id)
            ).all()
            
            # Calcular métricas
            total = len(cases)
            active = len([c for c in cases if c.status == 'activo'])
            urgent = len([c for c in cases if c.status == 'urgente'])
            pending = len([c for c in cases if c.status == 'pendiente'])
            
            return {
                "total": total,
                "active": active,
                "urgent": urgent,
                "pending": pending
            }

    @staticmethod
    def update_case(case_id: int, case_data: dict, user: User):
        """Actualiza un caso completo"""
        with SessionLocal() as session:
            legal_case = LegalCaseService._fetch_case(case_id, user, session)
            if not legal_case:
                return False
            
            # Actualizar campos permitidos
            allowed_fields = ['title', 'case_type', 'status', 'priority_level', 'description', 'notes', 'end_date']
            
            for field, value in case_data.items():
                if field in allowed_fields and hasattr(legal_case, field):
                    setattr(legal_case, field, value)
            
            session.commit()
            return LegalCaseOut.model_validate(legal_case)
        
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
    def upload_file_to_storage(filename,  file: UploadFile, storage: Storage) -> bool:
        """Upload to a blob storage"""
        response = storage.upload(file.file, filename)
        return response
        
    @staticmethod
    def has_available_storage(case_id: int, file: UploadFile) -> bool:
        """Check if the account has available storage to upload files"""
        # TODO: Check if the account has available storage
        return True
    
    @staticmethod
    def file_exists(case_id: int, file: UploadFile) -> bool:
        """Check if the file already exists in the case"""
        with SessionLocal() as sesssion:
            return sesssion.query(LegalCase).filter(LegalCase.id == case_id, LegalCase.files.any(File.file_name == file.filename)).first()
        
    @staticmethod
    def get_file(file_id: int, storage: Storage):    
        """Get a file from the given Blob Storage"""
        with SessionLocal() as session:
            file = session.query(File).filter(File.id == file_id).first()
            filepath = file.file_path
            filename = file.file_name
        file_stream, content_type = storage.get(filepath)
        if not file_stream:
            return False, False
        return file_stream, content_type
    
    @staticmethod
    def save_file(case_id: int,  user: User, file: UploadFile):
        """Save a files's data in DB"""
        with SessionLocal() as session:
            file = File(
                file_name = file.filename,
                file_path = f"{case_id}/{file.filename}",
                upload_date=datetime.now(),
                status=StatusEnum.ACTIVE,
                # Save the size of the file in MB
                size_mb= float(file.size / 1024)
            )
            legal_case = LegalCaseService._fetch_case(case_id, user, session)
            legal_case.files.add(file)
            session.add(file)
            session.commit()
            return FileOut.model_validate(file)

            
    @staticmethod
    def _fetch_case(case_id, user: User, session) -> LegalCase:
        """Fetch a case injecting a session"""
        # TODO: Add a status in legal_case_x_users to consider access management to the case.
        return session.query(LegalCase).filter(LegalCase.id == case_id, LegalCase.users.any(User.id == user.id)).first()