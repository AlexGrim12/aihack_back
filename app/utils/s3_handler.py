import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from app.config import settings
from typing import BinaryIO

class S3Handler:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.AWS_S3_BUCKET
    
    def upload_image(self, file: BinaryIO, filename: str) -> str:
        """
        Sube una imagen a S3 y retorna la URL pública
        
        Args:
            file: Archivo binario de la imagen
            filename: Nombre del archivo
        
        Returns:
            URL pública de la imagen en S3
        
        Raises:
            Exception: Si hay error al subir la imagen
        """
        try:
            # Generar nombre único para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
            s3_key = f"fall-detections/{timestamp}_{unique_id}.{file_extension}"
            
            # Subir archivo a S3
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': f'image/{file_extension}',
                    'ACL': 'public-read'  # Hacer la imagen pública
                }
            )
            
            # Generar URL pública
            image_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
            
            return image_url
            
        except ClientError as e:
            raise Exception(f"Error al subir imagen a S3: {str(e)}")
    
    def delete_image(self, image_url: str) -> bool:
        """
        Elimina una imagen de S3 dado su URL
        
        Args:
            image_url: URL completa de la imagen en S3
        
        Returns:
            True si se eliminó exitosamente
        """
        try:
            # Extraer key del URL
            s3_key = image_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[1]
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
            
        except ClientError as e:
            raise Exception(f"Error al eliminar imagen de S3: {str(e)}")

# Instancia global del manejador de S3
s3_handler = S3Handler()
