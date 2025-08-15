"""Abstract class for Blob Storage implementations"""
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def get(self, filename):
        """Get a file from the blob storage"""
        pass

    @abstractmethod
    def delete(self, file):
        """Delete a file from the blob storage"""
        pass

    @abstractmethod
    def upload(self, file, object_name):
        """Upload a file to the blob storage"""
        pass