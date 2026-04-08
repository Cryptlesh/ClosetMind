import os
import shutil
from typing import Optional
from fastapi import UploadFile
import logging
from app.core.settings import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.use_gcs = os.getenv("USE_GCS", "false").lower() == "true"
        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        
        if not self.use_gcs:
            self.upload_dir = "uploads"
            if not os.path.exists(self.upload_dir):
                os.makedirs(self.upload_dir)

    async def save_file(self, file: UploadFile) -> str:
        """
        Saves a file and returns the accessible URL.
        """
        filename = file.filename
        
        if self.use_gcs:
            return await self._save_to_gcs(file, filename)
        else:
            return await self._save_to_local(file, filename)

    async def _save_to_local(self, file: UploadFile, filename: str) -> str:
        file_path = os.path.join(self.upload_dir, filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        logger.info(f"File saved locally: {file_path}")
        return f"uploads/{filename}"

    async def _save_to_gcs(self, file: UploadFile, filename: str) -> str:
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(f"closetmind/{filename}")
            
            content = await file.read()
            blob.upload_from_string(content, content_type=file.content_type)
            
            # Returns the public URL (assuming bucket permissions are set)
            return f"https://storage.googleapis.com/{self.bucket_name}/closetmind/{filename}"
        except Exception as e:
            logger.error(f"Failed to upload to GCS: {e}")
            # Fallback to local if GCS fails during dev
            return await self._save_to_local(file, filename)

storage_service = StorageService()
