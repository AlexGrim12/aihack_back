import os
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile

class AudioHandler:
    """
    Utility class for handling audio file storage.
    Similar to S3Handler but for local file storage.
    """
    
    def __init__(self, storage_path: str = "storage/incidents"):
        """
        Initialize the AudioHandler.
        
        Args:
            storage_path: Directory path where audio files will be stored
        """
        self.storage_path = storage_path
        # Create storage directory if it doesn't exist
        Path(storage_path).mkdir(parents=True, exist_ok=True)
    
    async def save_audio(self, audio_file: UploadFile, base_url: str = "http://localhost:8000") -> str:
        """
        Save an audio file to local storage.
        
        Args:
            audio_file: The uploaded audio file
            base_url: Base URL for constructing the audio URL
            
        Returns:
            str: Public URL to access the audio file
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # Get file extension
        file_extension = os.path.splitext(audio_file.filename)[1] if audio_file.filename else ".aac"
        
        # Construct filename
        filename = f"audio_{timestamp}_{unique_id}{file_extension}"
        file_path = os.path.join(self.storage_path, filename)
        
        # Save file
        content = await audio_file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Reset file pointer for potential reuse
        await audio_file.seek(0)
        
        # Return public URL
        return f"{base_url}/{self.storage_path}/{filename}"
    
    def delete_audio(self, audio_url: str) -> bool:
        """
        Delete an audio file from local storage.
        
        Args:
            audio_url: The URL of the audio file to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Extract filename from URL
            filename = audio_url.split("/")[-1]
            file_path = os.path.join(self.storage_path, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting audio file: {e}")
            return False

# Global instance
audio_handler = AudioHandler()
