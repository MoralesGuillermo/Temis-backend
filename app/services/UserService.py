"""User management service"""

from sqlalchemy.orm import joinedload

from app.database.database import SessionLocal
from app.database.models import User, Role, Account, Subscription
from app.schemas.UserProfileResponse import UserProfileResponse
from app.schemas.EditProfileRequest import EditProfileRequest, EditProfileResponse, ChangePasswordRequest, ChangePasswordResponse
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