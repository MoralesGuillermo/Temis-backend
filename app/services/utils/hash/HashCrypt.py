# External dependencies
from passlib.context import CryptContext

# Client dependencies
from app.services.utils.hash.Hash import Hash


class HashCrypt(Hash):
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, content) -> str:
        return self.pwd_context.hash(content)

    def verify(self, content, hashed) -> bool:
        return self.pwd_context.verify(content, hashed, scheme="bcrypt")