#!/bin/bash

# 🎤 Script de Prueba para Sistema de Reportes de Incidentes con Audio
# Este script prueba el endpoint inteligente que detecta automáticamente el flujo

set -e  # Exit on error

BASE_URL="http://localhost"
TEMP_AUDIO="/tmp/test_incident_audio.mp3"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🎤 Sistema de Reportes de Incidentes con Audio - Tests      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Crear audio de prueba con ffmpeg
echo -e "${YELLOW}📝 Creando archivo de audio de prueba...${NC}"

if command -v ffmpeg &> /dev/null; then
    # Crear un audio de 3 segundos con tono en formato MP3 (compatible con OpenAI Whisper)
    ffmpeg -f lavfi -i "sine=frequency=1000:duration=3" -acodec libmp3lame /tmp/test_incident_audio.mp3 -y > /dev/null 2>&1
    echo -e "${GREEN}✓ Audio de prueba creado: /tmp/test_incident_audio.mp3${NC}"
else
    echo -e "${RED}⚠️  ffmpeg no está instalado. Por favor instala ffmpeg para crear el audio de prueba.${NC}"
    echo -e "${YELLOW}   En macOS: brew install ffmpeg${NC}"
    echo -e "${YELLOW}   En Ubuntu: sudo apt-get install ffmpeg${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  TEST 1: Flujo Manual (Audio + Formulario Completo)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}📤 POST /reports/incident (con todos los campos)${NC}"
echo ""

CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")

curl -X POST "${BASE_URL}/reports/incident" \
  -F "audio=@${TEMP_AUDIO}" \
  -F "station=Observatorio, Línea 1" \
  -F "type=delay" \
  -F "level=medium" \
  -F "description=Retraso por falla en señalización" \
  -F "incident_datetime=${CURRENT_TIME}" \
  -w "\n\n" | python3 -m json.tool

echo ""
echo -e "${GREEN}✓ Test 1 completado - Flujo Manual${NC}"
echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  TEST 2: Flujo Automático (Solo Audio con IA)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}⚠️  NOTA: Este test requiere OpenAI API Key configurada${NC}"
echo -e "${YELLOW}    Si no está configurada, verás un error.${NC}"
echo ""
echo -e "${YELLOW}📤 POST /reports/incident (solo audio, sin campos)${NC}"
echo ""

curl -X POST "${BASE_URL}/reports/incident" \
  -F "audio=@${TEMP_AUDIO}" \
  -w "\n\n" | python3 -m json.tool 2>&1 || echo -e "${RED}⚠️  Error: Verifica que OPENAI_API_KEY esté configurada${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  TEST 3: Listar Reportes${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}📤 GET /reports/incident${NC}"
echo ""

curl -X GET "${BASE_URL}/reports/incident" \
  -w "\n\n" | python3 -m json.tool

echo ""
echo -e "${GREEN}✓ Test 3 completado${NC}"
echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  📋 Guía de Uso${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

cat << 'EOF'
📖 ENDPOINT INTELIGENTE:

✨ POST /reports/incident
   
   Este endpoint detecta automáticamente el flujo:
   
   🔹 FLUJO A - Solo Audio (Transcripción con IA):
      Si NO envías station, type, level → Usa OpenAI para extraer datos
      
      Ejemplo:
      curl -X POST http://localhost:8000/reports/incident \
        -F "audio=@mi_audio.aac"
   
   🔹 FLUJO B - Audio + Formulario (Manual):
      Si envías station, type, level → Guarda los datos del formulario
      
      Ejemplo:
      curl -X POST http://localhost:8000/reports/incident \
        -F "audio=@mi_audio.aac" \
        -F "station=Observatorio" \
        -F "type=delay" \
        -F "level=medium" \
        -F "description=Descripción opcional" \
        -F "incident_datetime=2024-01-20T14:30:00.000Z"

📖 PARÁMETROS:

   - audio: archivo de audio (AAC, MP3, WAV, etc.) [REQUERIDO]
   - station: estación/ubicación [OPCIONAL - si no se envía, usa IA]
   - type: delay | incident | maintenance | crowding | other [OPCIONAL - si no se envía, usa IA]
   - level: low | medium | high | critical [OPCIONAL - si no se envía, usa IA]
   - description: descripción adicional [OPCIONAL]
   - incident_datetime: fecha/hora ISO 8601 [OPCIONAL - si no se envía, usa IA o fecha actual]

📖 OTROS ENDPOINTS:

   GET /reports/incident?skip=0&limit=100  → Listar reportes
   GET /reports/incident/{id}              → Obtener reporte específico
   DELETE /reports/incident/{id}           → Eliminar reporte

📝 TIPOS DE INCIDENTE (type):
   - delay: Retrasos, demoras
   - incident: Incidentes, emergencias
   - maintenance: Mantenimiento, fallas técnicas
   - crowding: Aglomeración, sobrecupo
   - other: Otros

📊 NIVELES DE SEVERIDAD (level):
   - low: Bajo (afectación mínima)
   - medium: Medio (afectación moderada)
   - high: Alto (afectación importante)
   - critical: Crítico (emergencia)

🔑 CONFIGURACIÓN DE OPENAI:
   Para usar la transcripción automática, configura en .env:
   
   OPENAI_API_KEY=sk-your-api-key-here


   Obtén tu API key en: https://platform.openai.com/api-keys

🎯 FLUJO DE USO RECOMENDADO:

   Opción A: Transcripción Automática
   1. Usuario graba audio narrando el incidente
   2. Flutter envía solo el audio a /reports/incident/automatic
   3. Backend transcribe con Whisper y extrae datos con GPT
   4. Retorna todos los campos extraídos automáticamente

   Opción B: Llenado Manual
   1. Usuario graba audio narrando el incidente
   2. Usuario llena formulario con los detalles
   3. Flutter envía audio + formulario a /reports/incident/manual
   4. Backend guarda el audio y los datos proporcionados

EOF

echo ""
echo -e "${GREEN}✓ Tests completados exitosamente${NC}"
echo ""
