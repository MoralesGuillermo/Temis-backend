"""User management service"""
#esa onda es comentario o cómo?

from sqlalchemy.orm import joinedload

from app.database.database import SessionLocal
from app.database.models import User, Role, Account, Subscription
from app.schemas.UserProfileResponse import UserProfileResponse

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