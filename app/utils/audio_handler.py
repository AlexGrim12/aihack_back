import os
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile
import boto3
from botocore.exceptions import ClientError
from app.config import settings

class AudioHandler:
    """
    Utility class for handling audio file storage.
    Supports both S3 and local file storage.
    """
    
    def __init__(self, storage_path: str = "storage/incidents", use_s3: bool = True):
        """
        Initialize the AudioHandler.
        
        Args:
            storage_path: Directory path for local storage (used as fallback or when S3 is disabled)
            use_s3: Whether to use S3 for storage (default: True)
        """
        self.storage_path = storage_path
        self.use_s3 = use_s3 and hasattr(settings, 'AWS_ACCESS_KEY_ID') and settings.AWS_ACCESS_KEY_ID
        
        if self.use_s3:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
                self.bucket_name = settings.AWS_S3_BUCKET
                print(f"✅ AudioHandler initialized with S3 storage (bucket: {self.bucket_name})")
            except Exception as e:
                print(f"⚠️ Failed to initialize S3, falling back to local storage: {e}")
                self.use_s3 = False
        
        if not self.use_s3:
            # Create local storage directory if it doesn't exist
            Path(storage_path).mkdir(parents=True, exist_ok=True)
            print(f"✅ AudioHandler initialized with local storage (path: {storage_path})")
    
    async def save_audio(self, audio_file: UploadFile, base_url: str = "http://localhost:8000") -> str:
        """
        Save an audio file to S3 or local storage.
        
        Args:
            audio_file: The uploaded audio file
            base_url: Base URL for constructing the audio URL (used for local storage)
            
        Returns:
            str: Public URL to access the audio file
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # Get file extension
        file_extension = os.path.splitext(audio_file.filename)[1] if audio_file.filename else ".wav"
        
        # Construct filename
        filename = f"audio_{timestamp}_{unique_id}{file_extension}"
        
        # Read file content
        content = await audio_file.read()
        
        if self.use_s3:
            # Upload to S3
            try:
                s3_key = f"incidents/{filename}"
                
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=content,
                    ContentType=audio_file.content_type or "audio/wav"
                )
                
                # Return S3 URL
                audio_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
                print(f"✅ Audio uploaded to S3: {audio_url}")
                return audio_url
                
            except ClientError as e:
                print(f"❌ S3 upload failed: {e}, falling back to local storage")
                # Fall back to local storage on error
                self.use_s3 = False
        
        # Local storage (fallback or default)
        file_path = os.path.join(self.storage_path, filename)
        with open(file_path, "wb") as f:
            f.write(content)
        # Local storage (fallback or default)
        file_path = os.path.join(self.storage_path, filename)
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Reset file pointer for potential reuse
        await audio_file.seek(0)
        
        # Return public URL
        audio_url = f"{base_url}/storage/{self.storage_path.split('/')[-1]}/{filename}"
        print(f"✅ Audio saved locally: {audio_url}")
        return audio_url
    
    def delete_audio(self, audio_url: str) -> bool:
        """
        Delete an audio file from S3 or local storage.
        
        Args:
            audio_url: The URL of the audio file to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            if self.use_s3 and "s3.amazonaws.com" in audio_url:
                # Delete from S3
                # Extract key from URL: https://bucket.s3.region.amazonaws.com/key
                s3_key = audio_url.split(".amazonaws.com/")[1]
                
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=s3_key
                )
                print(f"✅ Deleted from S3: {s3_key}")
                return True
            else:
                # Delete from local storage
                filename = audio_url.split("/")[-1]
                file_path = os.path.join(self.storage_path, filename)
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"✅ Deleted locally: {filename}")
                    return True
                return False
        except Exception as e:
            print(f"❌ Error deleting audio file: {e}")
            return False

# Global instance
audio_handler = AudioHandler()
