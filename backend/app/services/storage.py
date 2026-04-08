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
        import uuid
        # Generate a unique filename to prevent collisions and handle empty browser filenames
        ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        if not ext: ext = ".jpg"
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # In cloud, we always save locally first to have a copy for internal processing,
        local_path = await self._save_to_local_disk(file, unique_filename)
        
        if self.use_gcs and self.bucket_name:
            gcs_url = await self._upload_to_gcs(local_path, unique_filename)
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

    async def ensure_local_file(self, url: str) -> Optional[str]:
        """
        Ensures a file is present on the local disk.
        If it's a GCS URL and missing locally, it downloads it.
        Returns the local relative path (e.g., uploads/filename.png).
        """
        if not url: return None
        
        # 1. Determine the filename from the URL
        filename = os.path.basename(url)
        local_path = os.path.join(self.upload_dir, filename)
        
        # 2. Check if already present locally
        if os.path.exists(local_path):
            return local_path
            
        # 3. If missing and it's a GCS URL, download it
        if "storage.googleapis.com" in url and self.use_gcs:
            try:
                from google.cloud import storage
                client = storage.Client()
                bucket = client.bucket(self.bucket_name)
                # Parse blob name (closetmind/filename)
                # URL format: .../bucket_name/closetmind/filename
                blob_name = f"closetmind/{filename}"
                blob = bucket.blob(blob_name)
                
                logger.info(f"Downloading {blob_name} from GCS for local processing...")
                blob.download_to_filename(local_path)
                return local_path
            except Exception as e:
                logger.error(f"Failed to download from GCS: {e}")
                
        # 4. If it's a relative path to begin with
        if url.startswith("uploads/"):
            return url.replace("/", os.sep)
            
        return None

storage_service = StorageService()
