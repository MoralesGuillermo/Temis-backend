from abc import ABC, abstractmethod

class Hash(ABC):
    @abstractmethod
    def hash(self, content) -> str:
        """Implement a hash algorithm here"""
        pass

    @abstractmethod
    def verify(self, content, hashed) -> bool:
        """Implement if an unhashed content and a hashed content are equals"""
        pass