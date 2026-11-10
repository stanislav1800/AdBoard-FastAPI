from pathlib import Path
import uuid

from fastapi import UploadFile

from app.storage.base import BaseStorage

class LocalStorage(BaseStorage):
    def __init__(self, upload_dir: str = './data/'):
        self.upload_dir = Path(upload_dir).resolve()
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, path: str | Path) -> Path:
        """Не даём выйти за пределы upload_dir (../, абсолютные пути)"""
        full_path = (self.upload_dir / path).resolve()
        if not full_path.is_relative_to(self.upload_dir):
            raise ValueError(f"Недопустимый путь: {path}")
        return full_path

    async def save(self, file: UploadFile, folder: str | None = None) -> str:
        folder_path = self.upload_dir
        if folder:
            folder_path = self._safe_path(folder)
            folder_path.mkdir(parents=True, exist_ok=True)

        suffix = Path(file.filename or "").suffix.lower()
        if not suffix[1:].isalnum():
            suffix = ""
        file_path = folder_path / f"{uuid.uuid4().hex}{suffix}"
        content = await file.read()

        # Сохраняем файл на volume
        with open(file_path, "wb") as f:
            f.write(content)

        return file_path.relative_to(self.upload_dir).as_posix()

    async def delete(self, path: str):
        file_path = self._safe_path(path)
        if file_path.is_file():
            file_path.unlink()
