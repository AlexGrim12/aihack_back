from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from dateutil import parser

from app.database import get_db
from app.models.incident_report import IncidentReport, IncidentType, IncidentLevel
from app.schemas.incident_report import (
    IncidentReportResponse,
    IncidentReportAutomaticResponse,
    IncidentReportManualCreate
)
from app.utils.audio_handler import audio_handler
from app.utils.openai_service import openai_service

router = APIRouter(prefix="/reports/incident", tags=["Incident Reports"])


@router.post("", response_model=IncidentReportResponse)
async def create_incident_report(
    audio: UploadFile = File(..., description="Audio file (AAC, MP3, WAV, etc.)"),
    station: Optional[str] = Form(None, description="Estación del incidente (opcional)"),
    type: Optional[str] = Form(None, description="Tipo: delay, incident, maintenance, crowding, other (opcional)"),
    level: Optional[str] = Form(None, description="Nivel: low, medium, high, critical (opcional)"),
    description: Optional[str] = Form(None, description="Descripción adicional (opcional)"),
    incident_datetime: Optional[str] = Form(None, description="Fecha/hora en formato ISO 8601 (opcional)"),
    db: Session = Depends(get_db)
):
    """
    ## 🎤 Endpoint Inteligente de Reportes de Incidentes
    
    **Detecta automáticamente el flujo:**
    
    ### Flujo A: Solo Audio (Transcripción con IA)
    Si NO se envían los campos del formulario (station, type, level):
    1. Recibe SOLO el archivo de audio
    2. Transcribe usando OpenAI Whisper
    3. Extrae información estructurada usando GPT-4
    4. Guarda el audio y los datos extraídos
    
    ### Flujo B: Audio + Formulario (Manual)
    Si se envían los campos del formulario:
    1. Recibe audio + campos completados
    2. Guarda el audio
    3. Guarda los datos proporcionados
    
    **Input:**
    - `audio`: Archivo de audio (REQUERIDO)
    - `station`: Estación (OPCIONAL - si no se envía, usa IA)
    - `type`: Tipo de incidente (OPCIONAL - si no se envía, usa IA)
    - `level`: Nivel de severidad (OPCIONAL - si no se envía, usa IA)
    - `description`: Descripción adicional (OPCIONAL)
    - `incident_datetime`: Fecha/hora ISO 8601 (OPCIONAL - si no se envía, usa IA o fecha actual)
    
    **Output:**
    - `audio_url`: URL del audio guardado
    - `station`: Estación del incidente
    - `type`: Tipo de incidente
    - `level`: Nivel de severidad
    - `description`: Descripción
    - `incident_datetime`: Fecha/hora del incidente
    - `message`: Mensaje de confirmación
    """
    
    # Validate audio file - be flexible with content type detection
    # Allow audio/* or common extensions if content type is missing/wrong
    allowed_extensions = ['.aac', '.mp3', '.wav', '.m4a', '.ogg', '.flac', '.wma', '.opus']
    file_extension = audio.filename.lower()[audio.filename.rfind('.'):] if '.' in audio.filename else ''
    
    is_valid_audio = (
        (audio.content_type and audio.content_type.startswith('audio/')) or
        file_extension in allowed_extensions
    )
    
    if not is_valid_audio:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only audio files are accepted. Received: {audio.content_type}, file: {audio.filename}"
        )
    
    try:
        # Save audio file first
        audio_url = await audio_handler.save_audio(audio)
        
        # Detectar el flujo: ¿Vienen los campos del formulario?
        is_manual = station is not None and type is not None and level is not None
        
        if is_manual:
            # FLUJO B: FORMULARIO MANUAL
            # Usuario llenó el formulario, solo guardamos los datos
            
            # Validate enum values
            try:
                incident_type = IncidentType(type)
                incident_level = IncidentLevel(level)
            except ValueError as e:
                audio_handler.delete_audio(audio_url)
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid type or level value: {str(e)}"
                )
            
            # Parse incident_datetime or use current time
            if incident_datetime:
                try:
                    incident_dt = parser.isoparse(incident_datetime)
                except ValueError:
                    audio_handler.delete_audio(audio_url)
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid datetime format. Use ISO 8601 format."
                    )
            else:
                incident_dt = datetime.now()
            
            # Save to database
            db_incident = IncidentReport(
                audio_url=audio_url,
                station=station,
                type=incident_type,
                level=incident_level,
                description=description if description else None,
                incident_datetime=incident_dt
            )
            
            db.add(db_incident)
            db.commit()
            db.refresh(db_incident)
            
            return IncidentReportResponse(
                audio_url=audio_url,
                station=station,
                type=type,
                level=level,
                description=description if description else "",
                incident_datetime=incident_dt,
                message="Reporte manual guardado exitosamente"
            )
        
        else:
            # FLUJO A: TRANSCRIPCIÓN AUTOMÁTICA CON IA
            # Usuario solo envió audio, usamos OpenAI para extraer datos
            
            # 1. Transcribe audio using Whisper
            transcription = await openai_service.transcribe_audio(audio)
            
            # 2. Extract structured data using GPT
            extracted_data = await openai_service.extract_incident_data(transcription)
            
            # 3. Parse incident_datetime
            incident_dt = parser.isoparse(extracted_data["incident_datetime"])
            
            # 4. Save to database
            db_incident = IncidentReport(
                audio_url=audio_url,
                station=extracted_data["station"],
                type=IncidentType(extracted_data["type"]),
                level=IncidentLevel(extracted_data["level"]),
                description=extracted_data.get("description") or "",
                incident_datetime=incident_dt
            )
            
            db.add(db_incident)
            db.commit()
            db.refresh(db_incident)
            
            # 5. Return response
            return IncidentReportResponse(
                audio_url=audio_url,
                station=extracted_data["station"],
                type=extracted_data["type"],
                level=extracted_data["level"],
                description=extracted_data.get("description") or "",
                incident_datetime=incident_dt,
                message=f"Reporte procesado automáticamente con IA. Transcripción: '{transcription[:100]}...'"
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Cleanup: delete audio if something fails
        if 'audio_url' in locals():
            audio_handler.delete_audio(audio_url)
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing incident report: {str(e)}"
        )


# ============================================================================
# ENDPOINTS DEPRECADOS (mantener por compatibilidad temporal)
# ============================================================================

@router.post("/automatic", response_model=IncidentReportResponse, deprecated=True)
async def create_incident_report_automatic_deprecated(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    ⚠️ DEPRECADO: Usa POST /reports/incident en su lugar.
    
    Este endpoint redirige al nuevo endpoint principal.
    """
    return await create_incident_report(
        audio=audio,
        station=None,
        type=None,
        level=None,
        description=None,
        incident_datetime=None,
        db=db
    )


@router.post("/manual", response_model=IncidentReportResponse, deprecated=True)
async def create_incident_report_manual_deprecated(
    audio: UploadFile = File(...),
    station: str = Form(...),
    type: str = Form(...),
    level: str = Form(...),
    description: Optional[str] = Form(""),
    incident_datetime: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    ⚠️ DEPRECADO: Usa POST /reports/incident en su lugar.
    
    Este endpoint redirige al nuevo endpoint principal.
    """
    return await create_incident_report(
        audio=audio,
        station=station,
        type=type,
        level=level,
        description=description,
        incident_datetime=incident_datetime,
        db=db
    )


# ============================================================================
# ENDPOINTS DE CONSULTA
# ============================================================================


@router.get("", response_model=list[IncidentReportResponse])
async def list_incident_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    ## 📋 Listar todos los reportes de incidentes
    
    Retorna una lista paginada de reportes ordenados por fecha del incidente (más reciente primero).
    """
    incidents = db.query(IncidentReport)\
        .order_by(IncidentReport.incident_datetime.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [
        IncidentReportResponse(
            audio_url=incident.audio_url,
            station=incident.station,
            type=incident.type.value,
            level=incident.level.value,
            description=incident.description if incident.description else "",
            incident_datetime=incident.incident_datetime,
            message=None
        )
        for incident in incidents
    ]


@router.get("/{incident_id}", response_model=IncidentReportResponse)
async def get_incident_report(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """
    ## 🔍 Obtener un reporte específico por ID
    """
    incident = db.query(IncidentReport).filter(IncidentReport.id == incident_id).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident report not found")
    
    return IncidentReportResponse(
        audio_url=incident.audio_url,
        station=incident.station,
        type=incident.type.value,
        level=incident.level.value,
        description=incident.description if incident.description else "",
        incident_datetime=incident.incident_datetime,
        message=None
    )


@router.delete("/{incident_id}")
async def delete_incident_report(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """
    ## 🗑️ Eliminar un reporte de incidente
    
    Elimina el reporte de la base de datos y el archivo de audio del storage.
    """
    incident = db.query(IncidentReport).filter(IncidentReport.id == incident_id).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident report not found")
    
    # Delete audio file
    audio_handler.delete_audio(incident.audio_url)
    
    # Delete from database
    db.delete(incident)
    db.commit()
    
    return {"message": "Incident report deleted successfully"}
