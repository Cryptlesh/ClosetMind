import os
import shutil
from typing import Optional
from fastapi import UploadFile
import logging
from app.core.settings import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        # Check if we should use GCS (preferred for cloud)
        self.use_gcs = os.getenv("USE_GCS", "false").lower() == "true"
        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        
        # Local fallback directory
        self.upload_dir = "uploads"
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    async def save_file(self, file: UploadFile) -> str:
        """
        Saves a file and returns the accessible path/URL.
        """
        # Ensure filename is clean
        filename = os.path.basename(file.filename)
        
        # In cloud, we always save locally first to have a copy for internal processing (like Gemini Vision),
        # but the "Public" URL we return depends on whether GCS is enabled.
        local_path = await self._save_to_local_disk(file, filename)
        
        if self.use_gcs and self.bucket_name:
            gcs_url = await self._upload_to_gcs(local_path, filename)
            if gcs_url:
                return gcs_url
        
        # If not using GCS or GCS fails, return the relative local path
        return f"uploads/{filename}"

    async def _save_to_local_disk(self, file: UploadFile, filename: str) -> str:
        file_path = os.path.join(self.upload_dir, filename)
        # Reset file pointer if it was read before
        await file.seek(0)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        logger.info(f"File saved to local disk: {file_path}")
        return file_path

    async def _upload_to_gcs(self, local_path: str, filename: str) -> Optional[str]:
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(f"closetmind/{filename}")
            
            logger.info(f"Attempting GCS upload for: {filename}")
            blob.upload_from_filename(local_path)
            
            logger.info(f"SUCCESS: GCS upload for {filename}")
            return f"https://storage.googleapis.com/{self.bucket_name}/closetmind/{filename}"
        except Exception as e:
            logger.error(f"FAILURE: GCS upload for {filename}. Error: {e}")
            return None

    async def save_image(self, image, filename: str) -> str:
        """
        Saves a PIL Image object and returns the accessible path/URL.
        Used for AI-generated VTON results.
        """
        local_path = os.path.join(self.upload_dir, filename)
        image.save(local_path)
        logger.info(f"Generated image saved to local disk: {local_path}")

        if self.use_gcs and self.bucket_name:
            gcs_url = await self._upload_to_gcs(local_path, filename)
            if gcs_url:
                return gcs_url

        return f"uploads/{filename}"

storage_service = StorageService()
