from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.fall_detection import FallDetection
from app.schemas.fall_detection import (
    FallDetectionResponse,
    FallDetectionUploadResponse
)
from app.utils.s3_handler import s3_handler

router = APIRouter(prefix="/falldetection", tags=["Fall Detection"])

@router.post("", response_model=FallDetectionUploadResponse, status_code=status.HTTP_201_CREATED)
async def create_fall_detection(
    image: UploadFile = File(..., description="Imagen del incidente"),
    station: str = Form(..., description="Estación donde ocurrió el incidente"),
    detected_object: str = Form(..., description="Objeto detectado"),
    incident_datetime: str = Form(..., description="Fecha y hora del incidente (formato ISO 8601)"),
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo incidente de detección de caída
    
    Recibe:
    - **image**: Archivo de imagen del incidente
    - **station**: Nombre de la estación donde ocurrió
    - **detected_object**: Tipo de objeto detectado (ej: persona, bicicleta)
    - **incident_datetime**: Fecha y hora en formato ISO 8601 (ej: 2024-01-20T10:30:00)
    
    La imagen se sube a AWS S3 y la URL se guarda en la base de datos.
    """
    try:
        # Validar que sea una imagen
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser una imagen"
            )
        
        # Parsear fecha/hora
        try:
            incident_dt = datetime.fromisoformat(incident_datetime.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inválido. Use formato ISO 8601 (ej: 2024-01-20T10:30:00)"
            )
        
        # Subir imagen a S3
        try:
            image_url = s3_handler.upload_image(image.file, image.filename)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al subir imagen a S3: {str(e)}"
            )
        
        # Crear registro en base de datos
        fall_detection = FallDetection(
            image_url=image_url,
            station=station,
            detected_object=detected_object,
            incident_datetime=incident_dt
        )
        
        db.add(fall_detection)
        db.commit()
        db.refresh(fall_detection)
        
        return FallDetectionUploadResponse(
            message="Incidente registrado exitosamente",
            fall_detection=FallDetectionResponse.from_orm(fall_detection)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la solicitud: {str(e)}"
        )

@router.get("", response_model=List[FallDetectionResponse])
async def get_all_fall_detections(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de todos los incidentes de detección de caída
    
    Parámetros:
    - **skip**: Número de registros a saltar (para paginación)
    - **limit**: Número máximo de registros a retornar
    """
    fall_detections = db.query(FallDetection)\
        .order_by(FallDetection.incident_datetime.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [FallDetectionResponse.from_orm(fd) for fd in fall_detections]

@router.get("/{fall_detection_id}", response_model=FallDetectionResponse)
async def get_fall_detection(
    fall_detection_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles de un incidente específico por ID
    """
    fall_detection = db.query(FallDetection).filter(FallDetection.id == fall_detection_id).first()
    
    if not fall_detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incidente no encontrado"
        )
    
    return FallDetectionResponse.from_orm(fall_detection)

@router.delete("/{fall_detection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fall_detection(
    fall_detection_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un incidente y su imagen asociada de S3
    """
    fall_detection = db.query(FallDetection).filter(FallDetection.id == fall_detection_id).first()
    
    if not fall_detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incidente no encontrado"
        )
    
    # Eliminar imagen de S3
    try:
        s3_handler.delete_image(fall_detection.image_url)
    except Exception as e:
        # Log error pero continuar con eliminación de DB
        print(f"Error al eliminar imagen de S3: {str(e)}")
    
    # Eliminar de base de datos
    db.delete(fall_detection)
    db.commit()
    
    return None
