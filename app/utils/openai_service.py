import json
from typing import Dict, Any
from openai import OpenAI
from fastapi import UploadFile
from app.config import settings

class OpenAIService:
    """
    Service for OpenAI integrations: Whisper (transcription) and GPT (extraction).
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def transcribe_audio(self, audio_file: UploadFile) -> str:
        """
        Transcribe audio to text using OpenAI Whisper API.
        
        Args:
            audio_file: The uploaded audio file
            
        Returns:
            str: Transcribed text in Spanish
        """
        # Read audio file content
        audio_content = await audio_file.read()
        
        # Reset file pointer for potential reuse
        await audio_file.seek(0)
        
        # Create a file-like object for OpenAI
        audio_file_obj = ("audio.aac", audio_content, audio_file.content_type or "audio/aac")
        
        # Transcribe using Whisper
        transcript = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file_obj,
            language="es"  # Spanish
        )
        
        return transcript.text
    
    async def extract_incident_data(self, transcription: str) -> Dict[str, Any]:
        """
        Extract structured incident data from transcription using GPT.
        
        Args:
            transcription: The transcribed text
            
        Returns:
            Dict with keys: station, type, level, description, incident_datetime
        """
        prompt = f"""
Analiza el siguiente reporte de incidente del metro de la Ciudad de México y extrae la información en formato JSON.

Texto del reporte: "{transcription}"

Extrae la siguiente información:
- station: nombre de la estación y línea (ejemplo: "Observatorio, Línea 1" o "Pantitlán")
- type: DEBE ser uno de estos valores exactos: "delay", "incident", "maintenance", "crowding", "other"
- level: DEBE ser uno de estos valores exactos: "low", "medium", "high", "critical"
- description: descripción breve y clara del incidente (máximo 200 caracteres)
- incident_datetime: fecha y hora en formato ISO 8601 (ejemplo: "2024-01-20T14:30:00.000Z"). Si no se menciona una fecha específica, usa la fecha y hora actual.

REGLAS IMPORTANTES:
1. Para "type", analiza el contexto:
   - "delay" = retrasos, demoras, esperas largas
   - "incident" = accidentes, emergencias, problemas de seguridad
   - "maintenance" = mantenimiento, reparaciones, fallas técnicas
   - "crowding" = aglomeraciones, sobrecupo, mucha gente
   - "other" = otros casos que no encajen en las categorías anteriores

2. Para "level", evalúa la gravedad:
   - "low" = problemas menores, sin afectación significativa
   - "medium" = afectación moderada, algunos retrasos
   - "high" = afectación importante, muchas personas afectadas
   - "critical" = emergencia, peligro, evacuación

3. Si no se puede determinar algún dato con certeza, usa valores razonables basados en el contexto.

Responde ÚNICAMENTE con el objeto JSON, sin texto adicional ni explicaciones.

Formato esperado:
{{
  "station": "Nombre de la estación",
  "type": "valor_exacto",
  "level": "valor_exacto",
  "description": "descripción del incidente",
  "incident_datetime": "2024-01-20T14:30:00.000Z"
}}
"""
        
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente experto en analizar reportes de incidentes del Sistema de Transporte Colectivo Metro de la Ciudad de México. Extraes información estructurada de forma precisa y concisa."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        # Parse JSON response
        response_text = completion.choices[0].message.content
        
        # Extract JSON from response (in case GPT adds extra text)
        try:
            # Try to parse directly
            extracted_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                extracted_data = json.loads(json_str)
            else:
                raise ValueError("Could not extract JSON from GPT response")
        
        # Validate required fields
        required_fields = ["station", "type", "level", "description", "incident_datetime"]
        for field in required_fields:
            if field not in extracted_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate enum values
        valid_types = ["delay", "incident", "maintenance", "crowding", "other"]
        valid_levels = ["low", "medium", "high", "critical"]
        
        if extracted_data["type"] not in valid_types:
            # Default to "other" if invalid
            extracted_data["type"] = "other"
        
        if extracted_data["level"] not in valid_levels:
            # Default to "medium" if invalid
            extracted_data["level"] = "medium"
        
        return extracted_data

# Global instance
openai_service = OpenAIService()
