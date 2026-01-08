from abc import ABC, abstractmethod

from fastapi import UploadFile

class BaseStorage(ABC):
    @abstractmethod
    async def save(self, file: UploadFile, filename: str | None = None) -> str:
        """
        Сохраняет файл и возвращает путь, по которому его можно открыть через nginx
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, path: str):
        """Удаляет файл по пути"""
        raise NotImplementedError
