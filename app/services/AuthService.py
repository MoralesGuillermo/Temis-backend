# Client Dependencies
"""App authenticatino and authorization service"""
from app.services.utils.hash.Hash import Hash
from app.database.database import SessionLocal
from app.database.models import User
from app.schemas.enums import Status
from app.schemas.RegisterRequest import RegisterRequest, RegisterResponse
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

    @staticmethod    
    def register(self, payload: RegisterRequest) -> RegisterResponse:
        """Register a new user"""
        with SessionLocal() as session:
            # Verificar que el DNI no exista
            existing_dni = session.query(User).filter(User.dni == payload.dni).first()
            if existing_dni:
                raise HTTPException(status_code=400, detail="El DNI ya está registrado")
            
            # Verificar que el username no exista
            existing_username = session.query(User).filter(User.username == payload.username).first()
            if existing_username:
                raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
            
            # Verificar que el email no exista
            existing_email = session.query(User).filter(User.email == payload.email).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="El email ya está registrado")
            
            # Verificar que el número de asociación no exista
            existing_association = session.query(User).filter(User.association == payload.association).first()
            if existing_association:
                raise HTTPException(status_code=400, detail="El número de colegiatura ya está registrado")
            
            # Hashear la contraseña
            hashed_password = self.hash_service.hash(payload.password)
            
            # Crear el nuevo usuario con account_id = 1 y role_id = 2 (Abogado por defecto) (Modificar esta lógica despues)
            #Nt: Deberiamos crear el account del bufete de una, por cuestiones de tiempo lo haremos despues
            new_user = User(
                dni=payload.dni,
                username=payload.username,
                password=hashed_password,
                email=payload.email,
                first_name=payload.first_name,
                last_name=payload.last_name,
                association=payload.association,
                phone=payload.phone,
                city=payload.city,
                status=StatusEnum.ACTIVE,
                account_id=1,  # Account ID quemado
                role_id=2  # Role ID por defecto (Abogado)
            )
            
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            
            return RegisterResponse(
                id=new_user.id,
                dni=new_user.dni,
                username=new_user.username,
                email=new_user.email,
                first_name=new_user.first_name,
                last_name=new_user.last_name,
                association=new_user.association,
                phone=new_user.phone,
                city=new_user.city,
                message="Usuario registrado correctamente"
            )