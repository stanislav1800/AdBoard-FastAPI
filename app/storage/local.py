from pathlib import Path

from fastapi import UploadFile

from app.storage.base import BaseStorage

class LocalStorage(BaseStorage):
    def __init__(self, upload_dir: str = './data/'):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, file: UploadFile, folder: str | None = None) -> str:
        folder_path = self.upload_dir
        if folder:
            folder_path = folder_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)

        file_path = folder_path / file.filename
        content = await file.read()

        # Сохраняем файл на volume
        with open(file_path, "wb") as f:
            f.write(content)

        return str(file_path.relative_to(self.upload_dir))

    async def delete(self, path: str):
        file_path = self.upload_dir / path
        if file_path.exists():
            file_path.unlink()
