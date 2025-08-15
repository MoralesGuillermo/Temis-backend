"""Client management service"""
from sqlalchemy.sql import select, exists

from app.database.database import SessionLocal
from app.database.models import User, Client, Account

class ClientService:
    @staticmethod
    def get_client(id: int, session):
        return session.query(Client).filter(Client.id == id).first()
    
    @staticmethod
    def get_client_by_dni(client_dni: str, user: User) -> Client:
        """Return a firm's client using its DNI"""
        with SessionLocal() as session:
            account = user.account
            return session.query(Client).filter(Client.dni == client_dni, Client.accounts.any(Account.id == account.id)).first()
        
    @staticmethod
    def new_client(data):
        """Return a new client instance using its data"""
        return Client(
            first_name=data.first_name, 
            last_name=data.last_name,
            phone_1=data.phone_1,
            email=data.email,
            dni=data.dni,
            gender="N/A",
            address=data.address
        )