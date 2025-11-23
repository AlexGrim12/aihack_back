from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class FallDetectionCreate(BaseModel):
    station: str = Field(..., description="Estación donde ocurrió el incidente")
    detected_object: str = Field(..., description="Objeto detectado (ej: persona, bicicleta, etc)")
    incident_datetime: datetime = Field(..., description="Fecha y hora del incidente")

class FallDetectionResponse(BaseModel):
    id: int
    image_url: str
    station: str
    detected_object: str
    incident_datetime: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class FallDetectionUploadResponse(BaseModel):
    message: str
    fall_detection: FallDetectionResponse
