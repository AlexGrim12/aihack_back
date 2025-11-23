# 🎤 Sistema de Reportes de Incidentes con Audio - Documentación

## 📋 Resumen

Sistema completo de reporte de incidentes con **DOS FLUJOS SEPARADOS**:

1. **Transcripción Automática con IA**: El usuario graba audio, el backend transcribe y extrae información usando OpenAI
2. **Llenado Manual**: El usuario graba audio y llena un formulario con los detalles

---

## 🏗️ Arquitectura del Backend

### Archivos Creados

```
app/
├── models/
│   └── incident_report.py          # Modelo SQLAlchemy con enums
├── routes/
│   └── incident_reports.py         # 2 endpoints principales + CRUD
├── schemas/
│   └── incident_report.py          # Pydantic schemas para validación
└── utils/
    ├── audio_handler.py            # Almacenamiento local de audio
    └── openai_service.py           # Integración con Whisper + GPT-4
```

### Base de Datos

**Tabla: `incident_reports`**

| Campo               | Tipo     | Descripción                                   |
| ------------------- | -------- | --------------------------------------------- |
| `id`                | Integer  | Primary key                                   |
| `audio_url`         | String   | URL del audio guardado                        |
| `station`           | String   | Estación/ubicación                            |
| `type`              | Enum     | delay, incident, maintenance, crowding, other |
| `level`             | Enum     | low, medium, high, critical                   |
| `description`       | Text     | Descripción del incidente (nullable)          |
| `incident_datetime` | DateTime | Fecha/hora del incidente                      |
| `created_at`        | DateTime | Timestamp de creación                         |
| `updated_at`        | DateTime | Timestamp de actualización                    |

---

## 📡 Endpoints API

### 1️⃣ POST /reports/incident/automatic

**Endpoint de Transcripción Automática con OpenAI**

**Request:**

```http
POST /reports/incident/automatic
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="audio"; filename="audio.aac"
Content-Type: audio/aac

[binary audio data]
--boundary--
```

**Parámetros:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `audio` | File | ✅ Sí | Archivo de audio (AAC, MP3, WAV, etc.) |

**Flujo interno:**

1. Valida que el archivo sea de tipo audio
2. Guarda el audio en `storage/incidents/`
3. Transcribe el audio usando **OpenAI Whisper API**
4. Extrae datos estructurados usando **OpenAI GPT-4**:
   - `station` - Estación mencionada
   - `type` - Tipo de incidente
   - `level` - Nivel de severidad
   - `description` - Descripción del incidente
   - `incident_datetime` - Fecha/hora
5. Guarda en la base de datos
6. Retorna respuesta con todos los campos extraídos

**Response (200 OK):**

```json
{
  "audio_url": "http://localhost:8000/storage/incidents/audio_20240120_143000_abc123.aac",
  "station": "Observatorio, Línea 1",
  "type": "delay",
  "level": "medium",
  "description": "Retraso por falla en señalización, tren detenido 5 minutos",
  "incident_datetime": "2024-01-20T14:30:00.000Z",
  "message": "Reporte procesado automáticamente con IA",
  "transcription": "Hola, estoy en la estación Observatorio de la Línea 1..."
}
```

**Errores:**

- `400 Bad Request` - Archivo no es audio
- `500 Internal Server Error` - Error en OpenAI o base de datos

---

### 2️⃣ POST /reports/incident/manual

**Endpoint de Llenado Manual con Formulario**

**Request:**

```http
POST /reports/incident/manual
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="audio"; filename="audio.aac"
Content-Type: audio/aac

[binary audio data]
--boundary
Content-Disposition: form-data; name="station"

Observatorio, Línea 1
--boundary
Content-Disposition: form-data; name="type"

delay
--boundary
Content-Disposition: form-data; name="level"

medium
--boundary
Content-Disposition: form-data; name="description"

Retraso por falla técnica
--boundary
Content-Disposition: form-data; name="incident_datetime"

2024-01-20T14:30:00.000Z
--boundary--
```

**Parámetros:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `audio` | File | ✅ Sí | Archivo de audio |
| `station` | String | ✅ Sí | Estación/ubicación (texto libre) |
| `type` | String | ✅ Sí | delay, incident, maintenance, crowding, other |
| `level` | String | ✅ Sí | low, medium, high, critical |
| `description` | String | ❌ No | Descripción adicional (opcional) |
| `incident_datetime` | String | ✅ Sí | Fecha/hora ISO 8601 |

**Flujo interno:**

1. Valida que el archivo sea de tipo audio
2. Valida que `type` y `level` sean valores permitidos
3. Parsea `incident_datetime` a formato DateTime
4. Guarda el audio en `storage/incidents/`
5. Guarda los datos en la base de datos
6. Retorna confirmación

**Response (200 OK):**

```json
{
  "audio_url": "http://localhost:8000/storage/incidents/audio_20240120_143000_abc123.aac",
  "station": "Observatorio, Línea 1",
  "type": "delay",
  "level": "medium",
  "description": "Retraso por falla técnica",
  "incident_datetime": "2024-01-20T14:30:00.000Z",
  "message": "Reporte manual guardado exitosamente"
}
```

**Errores:**

- `400 Bad Request` - Archivo no es audio, valores inválidos
- `500 Internal Server Error` - Error guardando

---

### 3️⃣ GET /reports/incident/

**Listar todos los reportes (paginado)**

**Request:**

```http
GET /reports/incident/?skip=0&limit=100
```

**Parámetros de query:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | Integer | 0 | Número de registros a saltar |
| `limit` | Integer | 100 | Máximo de registros a retornar |

**Response:**

```json
[
  {
    "audio_url": "http://localhost:8000/storage/incidents/audio_xxx.aac",
    "station": "Observatorio, Línea 1",
    "type": "delay",
    "level": "medium",
    "description": "Retraso por falla técnica",
    "incident_datetime": "2024-01-20T14:30:00.000Z"
  }
]
```

---

### 4️⃣ GET /reports/incident/{id}

**Obtener un reporte específico**

**Request:**

```http
GET /reports/incident/1
```

**Response:**

```json
{
  "audio_url": "http://localhost:8000/storage/incidents/audio_xxx.aac",
  "station": "Observatorio, Línea 1",
  "type": "delay",
  "level": "medium",
  "description": "Retraso por falla técnica",
  "incident_datetime": "2024-01-20T14:30:00.000Z"
}
```

**Errores:**

- `404 Not Found` - Reporte no existe

---

### 5️⃣ DELETE /reports/incident/{id}

**Eliminar un reporte**

**Request:**

```http
DELETE /reports/incident/1
```

**Flujo interno:**

1. Busca el reporte en la base de datos
2. Elimina el archivo de audio del storage
3. Elimina el registro de la base de datos

**Response:**

```json
{
  "message": "Incident report deleted successfully"
}
```

**Errores:**

- `404 Not Found` - Reporte no existe

---

## 🤖 Integración con OpenAI

### Servicios Utilizados

#### 1. OpenAI Whisper API (Transcripción)

**Endpoint:** `https://api.openai.com/v1/audio/transcriptions`

**Modelo:** `whisper-1`

**Configuración:**

- `language="es"` - Español
- Soporta múltiples formatos: AAC, MP3, WAV, M4A, OGG, etc.

**Código:**

```python
transcript = self.client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file_obj,
    language="es"
)
transcription_text = transcript.text
```

#### 2. OpenAI GPT-4 API (Extracción de Datos)

**Endpoint:** `https://api.openai.com/v1/chat/completions`

**Modelo:** `gpt-4`

**Prompt:**

```
Analiza el siguiente reporte de incidente del metro de la Ciudad de México
y extrae la información en formato JSON.

Texto del reporte: "{transcription}"

Extrae:
- station: nombre de la estación y línea
- type: delay | incident | maintenance | crowding | other
- level: low | medium | high | critical
- description: descripción breve del incidente
- incident_datetime: fecha/hora ISO 8601
```

**Configuración:**

- `temperature=0.3` - Respuestas más determinísticas
- `max_tokens=500` - Límite de respuesta

**Validación:**

- Verifica que todos los campos requeridos estén presentes
- Valida que `type` y `level` sean valores permitidos
- Si son inválidos, usa valores por default (`other`, `medium`)

---

## 📁 Almacenamiento de Audio

### AudioHandler

**Ubicación:** `app/utils/audio_handler.py`

**Directorio de storage:** `storage/incidents/`

**Formato de nombres:**

```
audio_YYYYMMDD_HHMMSS_UUID.extension
```

Ejemplo: `audio_20240120_143000_abc12345.aac`

**Métodos:**

```python
# Guardar audio
audio_url = await audio_handler.save_audio(audio_file)
# Retorna: "http://localhost:8000/storage/incidents/audio_xxx.aac"

# Eliminar audio
success = audio_handler.delete_audio(audio_url)
```

**Características:**

- Crea el directorio automáticamente si no existe
- Genera nombres únicos con timestamp + UUID
- Retorna URL pública para acceso directo
- Soporta cualquier extensión de audio

---

## 🔐 Configuración

### Variables de Entorno

**Archivo: `.env`**

```bash
# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key-here

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/aihack_db

# JWT (para otros endpoints)
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Docker Compose

**Archivo: `docker-compose.yml`**

```yaml
backend:
  environment:
    OPENAI_API_KEY: ${OPENAI_API_KEY:-sk-your-openai-api-key-here}
```

---

## 🧪 Testing

### Script Automatizado

**Ejecutar:**

```bash
./test_incident_reports.sh
```

**Incluye:**

1. Creación de audio de prueba con `ffmpeg`
2. Test de endpoint manual
3. Test de endpoint automático (requiere OpenAI API Key)
4. Listado de reportes
5. Guía de uso completa

### Test Manual con curl

**1. Crear audio de prueba:**

```bash
ffmpeg -f lavfi -i "sine=frequency=1000:duration=3" -acodec aac test_audio.aac
```

**2. Probar endpoint manual:**

```bash
curl -X POST http://localhost:8000/reports/incident/manual \
  -F "audio=@test_audio.aac" \
  -F "station=Observatorio, Línea 1" \
  -F "type=delay" \
  -F "level=medium" \
  -F "description=Retraso" \
  -F "incident_datetime=$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"
```

**3. Probar endpoint automático:**

```bash
curl -X POST http://localhost:8000/reports/incident/automatic \
  -F "audio=@test_audio.aac"
```

---

## 📊 Valores Permitidos

### Tipo de Incidente (`type`)

| Valor         | Etiqueta      | Descripción                                     | Uso en GPT                                        |
| ------------- | ------------- | ----------------------------------------------- | ------------------------------------------------- |
| `delay`       | Retraso       | Retrasos, demoras, esperas largas               | Menciones de "retraso", "demora", "tren detenido" |
| `incident`    | Incidente     | Accidentes, emergencias, problemas de seguridad | "Accidente", "emergencia", "herido"               |
| `maintenance` | Mantenimiento | Mantenimiento, reparaciones, fallas técnicas    | "Falla", "descompuesto", "reparación"             |
| `crowding`    | Aglomeración  | Aglomeraciones, sobrecupo, mucha gente          | "Lleno", "saturado", "mucha gente"                |
| `other`       | Otro          | Otros casos                                     | Default si no encaja en categorías anteriores     |

### Nivel de Severidad (`level`)

| Valor      | Etiqueta | Descripción                                      | Evaluación GPT                    |
| ---------- | -------- | ------------------------------------------------ | --------------------------------- |
| `low`      | Bajo     | Afectación mínima, sin impacto significativo     | Problemas menores, sin urgencia   |
| `medium`   | Medio    | Afectación moderada, algunos retrasos            | Retrasos de hasta 10 minutos      |
| `high`     | Alto     | Afectación importante, muchas personas afectadas | Retrasos largos, muchas personas  |
| `critical` | Crítico  | Emergencia, peligro, evacuación                  | Emergencias médicas, evacuaciones |

---

## 🚀 Deployment

### Requisitos para Producción

1. **OpenAI API Key**

   - Crear cuenta en https://platform.openai.com
   - Generar API key
   - Configurar en variables de entorno

2. **Storage de Audio**

   - Producción: Usar S3, Google Cloud Storage, etc.
   - Actual: Local storage en `storage/incidents/`

3. **Rate Limiting**

   - OpenAI tiene límites de requests
   - Implementar caché de transcripciones
   - Considerar cola de procesamiento

4. **Monitoreo**
   - Logs de errores de OpenAI
   - Métricas de uso de API
   - Alertas de errores

---

## 🐛 Troubleshooting

### Error: "Module 'openai' could not be resolved"

**Solución:**

```bash
pip install openai==1.12.0
# O reconstruir Docker
docker-compose up -d --build backend
```

### Error: "Invalid OpenAI API Key"

**Verificar:**

```bash
# En .env
OPENAI_API_KEY=sk-...

# Verificar que esté configurada
docker-compose exec backend env | grep OPENAI
```

### Error: "Audio file too large"

**Límites:**

- OpenAI Whisper: Máximo 25 MB
- Solución: Comprimir audio antes de enviar

### Error: "GPT response is not valid JSON"

**Causa:** GPT a veces agrega texto extra

**Solución:** El código ya maneja este caso extrayendo el JSON del texto

---

## 📚 Recursos

- **OpenAI Whisper API:** https://platform.openai.com/docs/guides/speech-to-text
- **OpenAI GPT-4 API:** https://platform.openai.com/docs/guides/text-generation
- **FastAPI File Upload:** https://fastapi.tiangolo.com/tutorial/request-files/
- **SQLAlchemy Enums:** https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.Enum

---

## ✅ Checklist de Implementación

**Backend:**

- [x] Modelo `IncidentReport` creado
- [x] Schemas Pydantic creados
- [x] `AudioHandler` para storage local
- [x] `OpenAIService` con Whisper + GPT-4
- [x] Endpoint `/reports/incident/automatic`
- [x] Endpoint `/reports/incident/manual`
- [x] Endpoints CRUD (GET, DELETE)
- [x] Configuración de OpenAI en `.env`
- [x] Router registrado en `main.py`
- [x] Storage directory configurado
- [x] Static files mounted

**Testing:**

- [x] Script de prueba `test_incident_reports.sh`
- [x] Documentación completa
- [x] Ejemplos de curl
- [x] Integración con Flutter documentada

**Documentación:**

- [x] README.md actualizado
- [x] Documentación detallada creada
- [x] Ejemplos de Flutter incluidos
- [x] Guía de configuración

---

## 🎯 Próximos Pasos

1. **Configurar OpenAI API Key** en `.env`
2. **Reconstruir backend:** `docker-compose up -d --build backend`
3. **Ejecutar tests:** `./test_incident_reports.sh`
4. **Integrar con Flutter** usando los ejemplos del README
5. **Opcional:** Migrar de storage local a S3 en producción

---

**¡Sistema de reportes de incidentes con audio completamente implementado! 🎉**
