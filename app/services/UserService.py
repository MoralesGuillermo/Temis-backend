"""User management service"""

from sqlalchemy.orm import joinedload

from app.database.database import SessionLocal
from app.database.models import User, Role, Account, Subscription
from app.schemas.UserProfileResponse import UserProfileResponse
from app.schemas.EditProfileRequest import EditProfileRequest, EditProfileResponse, ChangePasswordRequest, ChangePasswordResponse
from app.schemas.RegisterUserRequest import RegisterUserRequest, RegisterUserResponse
from app.services.utils.hash.HashCrypt import HashCrypt

class UserService:
    @staticmethod
    def get_user_profile(user: User) -> UserProfileResponse:
        """Return complete user profile information"""
        with SessionLocal() as session:
            # Obtener el usuario completo con todas las relaciones
            complete_user = (
                session.query(User)
                .options(
                    joinedload(User.role),
                    joinedload(User.account).joinedload(Account.subscription)
                )
                .filter(User.id == user.id)
                .first()
            )
            
            if not complete_user:
                return None
            
            return UserProfileResponse(
                id=complete_user.id,
                dni=complete_user.dni,
                username=complete_user.username,
                email=complete_user.email,
                first_name=complete_user.first_name,
                last_name=complete_user.last_name,
                association=complete_user.association,
                phone=complete_user.phone,
                city=complete_user.city,
                status=complete_user.status.value,
                role_name=complete_user.role.name,
                account_email=complete_user.account.email,
                subscription_plan=complete_user.account.subscription.plan_name
            )

    @staticmethod
    def edit_profile(payload: EditProfileRequest, user: User) -> EditProfileResponse:
        """Update user profile information"""
        with SessionLocal() as session:
            # Obtener el usuario actual
            current_user = session.query(User).filter(User.id == user.id).first()
            
            if not current_user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            # Verificar si el email ya existe en otro usuario
            if payload.email != current_user.email:
                existing_user = session.query(User).filter(
                    User.email == payload.email,
                    User.id != user.id
                ).first()
                
                if existing_user:
                    raise HTTPException(status_code=400, detail="El email ya está en uso por otro usuario")
            
            # Actualizar los campos
            current_user.email = payload.email
            current_user.first_name = payload.first_name
            current_user.last_name = payload.last_name
            current_user.phone = payload.phone
            current_user.city = payload.city
            
            session.commit()
            session.refresh(current_user)
            
            return EditProfileResponse(
                id=current_user.id,
                email=current_user.email,
                first_name=current_user.first_name,
                last_name=current_user.last_name,
                phone=current_user.phone,
                city=current_user.city,
                message="Perfil actualizado correctamente"
            )
    
    @staticmethod
    def change_password(payload: ChangePasswordRequest, user: User) -> ChangePasswordResponse:
        """Change user password"""
        with SessionLocal() as session:
            # Obtener el usuario actual
            current_user = session.query(User).filter(User.id == user.id).first()
            
            if not current_user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            # Verificar la contraseña actual
            hash_service = HashCrypt()
            if not hash_service.verify(payload.current_password, current_user.password):
                raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
            
            # Validar que la nueva contraseña sea diferente
            if hash_service.verify(payload.new_password, current_user.password):
                raise HTTPException(status_code=400, detail="La nueva contraseña debe ser diferente a la actual")
            
            # Actualizar la contraseña
            current_user.password = hash_service.hash(payload.new_password)
            
            session.commit()
            
            return ChangePasswordResponse(
                message="Contraseña cambiada correctamente"
            )

    @staticmethod
    def register_user(payload: RegisterUserRequest, current_user: User) -> RegisterUserResponse:
        """Register a new user in the same account as the current user"""
        with SessionLocal() as session:
            # DNI único
            existing_dni = session.query(User).filter(User.dni == payload.dni).first()
            if existing_dni:
                raise HTTPException(status_code=400, detail="El DNI ya está registrado")
            
            # username único
            existing_username = session.query(User).filter(User.username == payload.username).first()
            if existing_username:
                raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
            
            # email único
            existing_email = session.query(User).filter(User.email == payload.email).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="El email ya está registrado")
            
            # número de asociación único (esto debe ser así?)
            existing_association = session.query(User).filter(User.association == payload.association).first()
            if existing_association:
                raise HTTPException(status_code=400, detail="El número de colegiatura ya está registrado")
            
            # rol existe
            role = session.query(Role).filter(Role.id == payload.role_id).first()
            if not role:
                raise HTTPException(status_code=400, detail="El rol especificado no existe")
            
            # Hashear la contraseña
            hash_service = HashCrypt()
            hashed_password = hash_service.hash(payload.password)
            
            # Crear el nuevo usuario
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
                account_id=current_user.account_id,  # Mismo account que el usuario actual (modificar despues)
                role_id=payload.role_id
            )
            
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            
            return RegisterUserResponse(
                id=new_user.id,
                dni=new_user.dni,
                username=new_user.username,
                email=new_user.email,
                first_name=new_user.first_name,
                last_name=new_user.last_name,
                association=new_user.association,
                phone=new_user.phone,
                city=new_user.city,
                role_name=role.name,
                message="Usuario registrado correctamente"
            )