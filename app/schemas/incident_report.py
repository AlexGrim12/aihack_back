from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class IncidentReportBase(BaseModel):
    station: str
    type: str
    level: str
    description: Optional[str] = None
    incident_datetime: datetime

class IncidentReportManualCreate(IncidentReportBase):
    """Schema para endpoint manual - recibe todos los campos del formulario"""
    pass

class IncidentReportResponse(BaseModel):
    audio_url: str
    station: str
    type: str
    level: str
    description: Optional[str] = None
    incident_datetime: datetime
    message: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class IncidentReportAutomaticResponse(BaseModel):
    """Response para endpoint automático - incluye datos extraídos por IA"""
    audio_url: str
    station: str
    type: str
    level: str
    description: str
    incident_datetime: datetime
    message: str
    transcription: Optional[str] = None  # Opcional: incluir la transcripción completa
