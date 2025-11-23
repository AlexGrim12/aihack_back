# AIHack Backend

Backend API desarrollado con FastAPI para aplicación Flutter, con autenticación JWT y PostgreSQL.

## 📦 Repositorios Relacionados

Este proyecto es parte de un ecosistema de aplicaciones para movilidad urbana inteligente:

- **[mobilityai](https://github.com/AlexGrim12/mobilityai)** - Aplicación móvil Flutter para usuarios finales del sistema de transporte
- **[mobilityAI_Operations_Dashboard](https://github.com/DavidFarfanC/mobilityAI_Operations_Dashboard)** - Dashboard de operaciones y monitoreo en tiempo real
- **[mobilityAI_fall_detection](https://github.com/ruyca/mobilityAI_fall_detection)** - Sistema de detección de caídas con visión por computadora

## Características

- 🔐 Autenticación JWT
- 🐘 Base de datos PostgreSQL con Docker
- 🚀 FastAPI con soporte async
- 🔒 Hash de contraseñas con bcrypt
- ✅ Validación de datos con Pydantic
- 🌐 CORS configurado para Flutter
- 🚇 **Simulación en tiempo real del Metro Línea 1**
- ⏱️ **Actualización automática cada 3 segundos**
- 📍 **20 estaciones reales con datos dinámicos**
- 📸 **Detección de caídas con almacenamiento en AWS S3**
- 🗄️ **Registro de incidentes en PostgreSQL**
- 🎤 **Reportes de incidentes con audio y transcripción automática**
- 🤖 **Integración con OpenAI (Whisper + GPT-4) para análisis de audio**

## Requisitos

- Python 3.9+
- Docker y Docker Compose
- pip
- **Cuenta de AWS con S3** (para almacenamiento de imágenes)
- **Cuenta de OpenAI** (para transcripción y análisis de audio)
- **ffmpeg** (opcional, para tests de audio)

## Instalación

### Opción 1: Con Docker (Recomendado)

1. **Asegúrate de tener Docker y Docker Compose instalados**

2. **Iniciar todos los servicios**

   ```bash
   docker-compose up -d
   ```

   Esto iniciará:

   - PostgreSQL en puerto 5432
   - Backend FastAPI en puerto 8000

3. **Ver logs**
   ```bash
   docker-compose logs -f backend
   ```

La API estará disponible en: `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

### Opción 2: Desarrollo Local

1. **Clonar el repositorio**

   ```bash
   cd aihack_back
   ```

2. **Crear entorno virtual**

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**

   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

5. **Iniciar PostgreSQL con Docker**

   ```bash
   docker-compose up -d postgres
   ```

6. **Ejecutar la aplicación**
   ```bash
   uvicorn main:app --reload
   ```

## Estructura del Proyecto

```
aihack_back/
├── app/
│   ├── models/          # Modelos de base de datos (SQLAlchemy)
│   ├── routes/          # Rutas/endpoints de la API
│   ├── schemas/         # Schemas de Pydantic para validación
│   ├── utils/           # Utilidades (JWT, seguridad)
│   ├── config.py        # Configuración de la aplicación
│   └── database.py      # Configuración de base de datos
├── docker-compose.yml   # Configuración de PostgreSQL
├── main.py              # Punto de entrada de la aplicación
├── requirements.txt     # Dependencias de Python
└── .env                 # Variables de entorno
```

## Endpoints de Autenticación

### Registro de Usuario

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### Obtener Usuario Actual

```http
GET /auth/me
Authorization: Bearer {token}
```

## Endpoints del Metro (Simulación en Tiempo Real)

### Estado de la Línea 1

```http
GET /metro/line1/status
```

**Response:**

```json
{
  "line_name": "Línea 1",
  "route": "Observatorio ↔ Pantitlán",
  "saturation": "medium",
  "incident_type": "none",
  "incident_message": null,
  "last_updated": "2024-01-20T10:30:00",
  "active_trains": [
    {
      "train_id": "T101",
      "current_station": "Observatorio",
      "next_station": "Tacubaya",
      "direction": "Pantitlán",
      "progress_to_next": 0.35,
      "wagons": 6,
      "passengers_per_wagon": [45, 52, 48, 50, 55, 47]
    }
  ]
}
```

### Estaciones de la Línea 1

```http
GET /metro/line1/stations
```

**Response:**

```json
[
  {
    "id": "observatorio",
    "name": "Observatorio",
    "latitude": 19.3986,
    "longitude": -99.2009,
    "saturation": "medium",
    "estimated_wait_time": 3,
    "has_incident": false,
    "incident_message": null,
    "people_waiting": 45,
    "next_train_arrival": 2
  }
]
```

### Reset de Simulación

```http
POST /metro/reset
```

**Response:**

```json
{
  "message": "Simulación reiniciada exitosamente",
  "timestamp": "2024-01-20T10:30:00"
}
```

### Características de la Simulación

- 🚇 **7 trenes activos** circulando simultáneamente
- ⏱️ **Actualización cada 3 segundos** en tiempo real
- 🔄 **Cambio automático de dirección** en las terminales
- 👥 **Ocupación dinámica** de vagones (20-60 pasajeros)
- ⚠️ **Incidentes aleatorios** (10% probabilidad)
- 📍 **20 estaciones** de la Línea 1 reales
- 📊 **Saturación calculada** basada en personas esperando

## Endpoints de Detección de Caídas

### Registrar Incidente

```http
POST /falldetection
Content-Type: multipart/form-data

- image: archivo de imagen
- station: "Observatorio"
- detected_object: "persona"
- incident_datetime: "2024-01-20T10:30:00"
```

**Response:**

```json
{
  "message": "Incidente registrado exitosamente",
  "fall_detection": {
    "id": 1,
    "image_url": "https://bucket.s3.region.amazonaws.com/fall-detections/20240120_103000_abc123.jpg",
    "station": "Observatorio",
    "detected_object": "persona",
    "incident_datetime": "2024-01-20T10:30:00",
    "created_at": "2024-01-20T10:30:05"
  }
}
```

### Listar Incidentes

```http
GET /falldetection?skip=0&limit=100
```

**Response:**

```json
[
  {
    "id": 1,
    "image_url": "https://bucket.s3.region.amazonaws.com/...",
    "station": "Observatorio",
    "detected_object": "persona",
    "incident_datetime": "2024-01-20T10:30:00",
    "created_at": "2024-01-20T10:30:05"
  }
]
```

### Obtener Incidente Específico

```http
GET /falldetection/{id}
```

### Eliminar Incidente

```http
DELETE /falldetection/{id}
```

**Nota:** Elimina el registro de la base de datos y la imagen de S3.

### Configuración de AWS S3

Para usar el endpoint de fall detection, configura las credenciales de AWS en `.env`:

```bash
AWS_ACCESS_KEY_ID=tu-access-key-id
AWS_SECRET_ACCESS_KEY=tu-secret-access-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=aihack-fall-detection
```

**Permisos requeridos en S3:**

- `s3:PutObject` - Para subir imágenes
- `s3:PutObjectAcl` - Para hacer imágenes públicas
- `s3:DeleteObject` - Para eliminar imágenes
- `s3:GetObject` - Para leer imágenes (opcional)

## Endpoints de Reportes de Incidentes con Audio

### 🎤 Sistema de Reportes con DOS FLUJOS:

#### 1️⃣ Endpoint de Transcripción Automática (Solo Audio + IA)

```http
POST /reports/incident/automatic
Content-Type: multipart/form-data

- audio: archivo de audio (AAC, MP3, WAV, etc.)
```

**Flujo:**

1. Recibe SOLO el archivo de audio
2. Transcribe usando OpenAI Whisper
3. Extrae información estructurada usando GPT-4
4. Guarda el audio y los datos extraídos
5. Retorna todos los campos extraídos

**Response:**

```json
{
  "audio_url": "http://localhost:8000/storage/incidents/audio_20240120_143000_abc123.aac",
  "station": "Observatorio, Línea 1",
  "type": "delay",
  "level": "medium",
  "description": "Retraso por falla en señalización",
  "incident_datetime": "2024-01-20T14:30:00.000Z",
  "message": "Reporte procesado automáticamente con IA",
  "transcription": "Hola, estoy en la estación Observatorio..."
}
```

#### 2️⃣ Endpoint de Llenado Manual (Audio + Formulario)

```http
POST /reports/incident/manual
Content-Type: multipart/form-data

- audio: archivo de audio
- station: "Observatorio, Línea 1"
- type: "delay"
- level: "medium"
- description: "Retraso por falla técnica" (opcional)
- incident_datetime: "2024-01-20T14:30:00.000Z"
```

**Flujo:**

1. Recibe audio + todos los campos del formulario
2. Guarda el audio
3. Guarda los datos en la base de datos
4. Retorna confirmación

**Response:**

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

### Otros Endpoints de Reportes

**Listar reportes:**

```http
GET /reports/incident/?skip=0&limit=100
```

**Obtener reporte específico:**

```http
GET /reports/incident/{id}
```

**Eliminar reporte:**

```http
DELETE /reports/incident/{id}
```

### Valores Permitidos para Reportes

**Tipos de Incidente (`type`):**

- `delay` - Retrasos, demoras
- `incident` - Incidentes, emergencias
- `maintenance` - Mantenimiento, fallas técnicas
- `crowding` - Aglomeración, sobrecupo
- `other` - Otros

**Niveles de Severidad (`level`):**

- `low` - Bajo (afectación mínima)
- `medium` - Medio (afectación moderada)
- `high` - Alto (afectación importante)
- `critical` - Crítico (emergencia)

### Configuración de OpenAI

Para usar el endpoint de transcripción automática, configura tu API key en `.env`:

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Obtén tu API key en:** https://platform.openai.com/api-keys

**Servicios utilizados:**

- **Whisper API** - Transcripción de audio a texto (español)
- **GPT-4 API** - Extracción de información estructurada

**Permisos requeridos en S3:**

- `s3:PutObject` - Para subir imágenes
- `s3:PutObjectAcl` - Para hacer imágenes públicas
- `s3:DeleteObject` - Para eliminar imágenes
- `s3:GetObject` - Para leer imágenes (opcional)

## Integración con Flutter

Para integrar este backend con tu app Flutter:

1. Instala el paquete `http` o `dio`:

   ```yaml
   dependencies:
     dio: ^5.0.0
   ```

2. Ejemplo de login en Flutter:

   ```dart
   import 'package:dio/dio.dart';

   class AuthService {
     final dio = Dio(BaseOptions(baseUrl: 'http://localhost:8000'));

     Future<Map<String, dynamic>> login(String email, String password) async {
       try {
         final response = await dio.post('/auth/login', data: {
           'email': email,
           'password': password,
         });
         return response.data;
       } catch (e) {
         throw Exception('Login failed: $e');
       }
     }
   }
   ```

3. Ejemplo de servicio de Reportes de Incidentes en Flutter:

   ```dart
   import 'package:dio/dio.dart';
   import 'dart:io';

   class IncidentReportService {
     final dio = Dio(BaseOptions(baseUrl: 'http://localhost:8000'));

     // Opción 1: Reporte automático con IA (solo audio)
     Future<Map<String, dynamic>> submitAutomaticReport({
       required File audioFile,
     }) async {
       try {
         final formData = FormData.fromMap({
           'audio': await MultipartFile.fromFile(
             audioFile.path,
             filename: audioFile.path.split('/').last,
           ),
         });

         final response = await dio.post(
           '/reports/incident/automatic',
           data: formData,
         );

         return response.data;
       } catch (e) {
         throw Exception('Failed to submit automatic report: $e');
       }
     }

     // Opción 2: Reporte manual (audio + formulario)
     Future<Map<String, dynamic>> submitManualReport({
       required File audioFile,
       required String station,
       required String type,
       required String level,
       String? description,
       required DateTime incidentDateTime,
     }) async {
       try {
         final formData = FormData.fromMap({
           'audio': await MultipartFile.fromFile(
             audioFile.path,
             filename: audioFile.path.split('/').last,
           ),
           'station': station,
           'type': type,
           'level': level,
           'description': description ?? '',
           'incident_datetime': incidentDateTime.toIso8601String(),
         });

         final response = await dio.post(
           '/reports/incident/manual',
           data: formData,
         );

         return response.data;
       } catch (e) {
         throw Exception('Failed to submit manual report: $e');
       }
     }

     // Obtener lista de reportes
     Future<List<dynamic>> getReports({int skip = 0, int limit = 100}) async {
       try {
         final response = await dio.get(
           '/reports/incident/',
           queryParameters: {'skip': skip, 'limit': limit},
         );
         return response.data;
       } catch (e) {
         throw Exception('Failed to get reports: $e');
       }
     }

     // Obtener reporte específico
     Future<Map<String, dynamic>> getReport(int id) async {
       try {
         final response = await dio.get('/reports/incident/$id');
         return response.data;
       } catch (e) {
         throw Exception('Failed to get report: $e');
       }
     }

     // Eliminar reporte
     Future<void> deleteReport(int id) async {
       try {
         await dio.delete('/reports/incident/$id');
       } catch (e) {
         throw Exception('Failed to delete report: $e');
       }
     }
   }
   ```

4. Ejemplo de servicio de Fall Detection en Flutter:

   ```dart
   import 'package:dio/dio.dart';
   import 'dart:io';

   class FallDetectionService {
     final dio = Dio(BaseOptions(baseUrl: 'http://localhost:8000'));

     // Enviar incidente con imagen
     Future<Map<String, dynamic>> reportIncident({
       required File imageFile,
       required String station,
       required String detectedObject,
       required DateTime incidentDateTime,
     }) async {
       try {
         // Crear FormData con multipart/form-data
         final formData = FormData.fromMap({
           'image': await MultipartFile.fromFile(
             imageFile.path,
             filename: imageFile.path.split('/').last,
           ),
           'station': station,
           'detected_object': detectedObject,
           'incident_datetime': incidentDateTime.toIso8601String(),
         });

         final response = await dio.post(
           '/falldetection',
           data: formData,
         );

         return response.data;
       } catch (e) {
         throw Exception('Failed to report incident: $e');
       }
     }

     // Obtener lista de incidentes
     Future<List<dynamic>> getIncidents({int skip = 0, int limit = 100}) async {
       try {
         final response = await dio.get(
           '/falldetection',
           queryParameters: {'skip': skip, 'limit': limit},
         );
         return response.data;
       } catch (e) {
         throw Exception('Failed to get incidents: $e');
       }
     }

     // Obtener incidente específico
     Future<Map<String, dynamic>> getIncident(int id) async {
       try {
         final response = await dio.get('/falldetection/$id');
         return response.data;
       } catch (e) {
         throw Exception('Failed to get incident: $e');
       }
     }

     // Eliminar incidente
     Future<void> deleteIncident(int id) async {
       try {
         await dio.delete('/falldetection/$id');
       } catch (e) {
         throw Exception('Failed to delete incident: $e');
       }
     }
   }
   ```

5. Ejemplo de uso en un Widget:

   ```dart
   import 'package:flutter/material.dart';
   import 'package:image_picker/image_picker.dart';
   import 'dart:io';

   class ReportIncidentScreen extends StatefulWidget {
     @override
     _ReportIncidentScreenState createState() => _ReportIncidentScreenState();
   }

   class _ReportIncidentScreenState extends State<ReportIncidentScreen> {
     final FallDetectionService _service = FallDetectionService();
     final ImagePicker _picker = ImagePicker();
     File? _imageFile;
     String _station = 'Observatorio';
     String _detectedObject = 'persona';
     bool _isLoading = false;

     Future<void> _pickImage() async {
       final XFile? image = await _picker.pickImage(source: ImageSource.camera);
       if (image != null) {
         setState(() {
           _imageFile = File(image.path);
         });
       }
     }

     Future<void> _submitReport() async {
       if (_imageFile == null) {
         ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Por favor selecciona una imagen')),
         );
         return;
       }

       setState(() {
         _isLoading = true;
       });

       try {
         final result = await _service.reportIncident(
           imageFile: _imageFile!,
           station: _station,
           detectedObject: _detectedObject,
           incidentDateTime: DateTime.now(),
         );

         ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text(result['message'])),
         );

         Navigator.pop(context);
       } catch (e) {
         ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Error: $e')),
         );
       } finally {
         setState(() {
           _isLoading = false;
         });
       }
     }

     @override
     Widget build(BuildContext context) {
       return Scaffold(
         appBar: AppBar(title: Text('Reportar Incidente')),
         body: Padding(
           padding: EdgeInsets.all(16),
           child: Column(
             children: [
               // Selector de imagen
               if (_imageFile != null)
                 Image.file(_imageFile!, height: 200)
               else
                 Container(
                   height: 200,
                   color: Colors.grey[300],
                   child: Center(child: Text('Sin imagen')),
                 ),
               SizedBox(height: 16),
               ElevatedButton(
                 onPressed: _pickImage,
                 child: Text('Tomar Foto'),
               ),
               SizedBox(height: 16),

               // Selector de estación
               DropdownButtonFormField<String>(
                 value: _station,
                 items: [
                   'Observatorio',
                   'Tacubaya',
                   'Juanacatlán',
                   // ... más estaciones
                 ].map((station) {
                   return DropdownMenuItem(
                     value: station,
                     child: Text(station),
                   );
                 }).toList(),
                 onChanged: (value) {
                   setState(() {
                     _station = value!;
                   });
                 },
                 decoration: InputDecoration(labelText: 'Estación'),
               ),

               // Selector de objeto detectado
               DropdownButtonFormField<String>(
                 value: _detectedObject,
                 items: [
                   'persona',
                   'bicicleta',
                   'maleta',
                   'otro',
                 ].map((obj) {
                   return DropdownMenuItem(
                     value: obj,
                     child: Text(obj),
                   );
                 }).toList(),
                 onChanged: (value) {
                   setState(() {
                     _detectedObject = value!;
                   });
                 },
                 decoration: InputDecoration(labelText: 'Objeto Detectado'),
               ),

               SizedBox(height: 24),

               // Botón de envío
               ElevatedButton(
                 onPressed: _isLoading ? null : _submitReport,
                 child: _isLoading
                     ? CircularProgressIndicator()
                     : Text('Reportar Incidente'),
               ),
             ],
           ),
         ),
       );
     }
   }
   ```

   ```

   ```

6. Ejemplo de servicio del Metro en Flutter:

   ```dart
   import 'package:dio/dio.dart';
   import 'dart:async';

   class MetroService {
     final dio = Dio(BaseOptions(baseUrl: 'http://localhost:8000'));
     Timer? _pollingTimer;

     // Obtener estado de la línea en tiempo real
     Future<Map<String, dynamic>> getLineStatus() async {
       try {
         final response = await dio.get('/metro/line1/status');
         return response.data;
       } catch (e) {
         throw Exception('Failed to get line status: $e');
       }
     }

     // Obtener estaciones
     Future<List<dynamic>> getStations() async {
       try {
         final response = await dio.get('/metro/line1/stations');
         return response.data;
       } catch (e) {
         throw Exception('Failed to get stations: $e');
       }
     }

     // Polling cada 3 segundos para actualizar UI
     void startPolling(Function(Map<String, dynamic>) onUpdate) {
       _pollingTimer = Timer.periodic(Duration(seconds: 3), (timer) async {
         try {
           final data = await getLineStatus();
           onUpdate(data);
         } catch (e) {
           print('Polling error: $e');
         }
       });
     }

     void stopPolling() {
       _pollingTimer?.cancel();
       _pollingTimer = null;
     }

     // Reset simulación
     Future<void> resetSimulation() async {
       try {
         await dio.post('/metro/reset');
       } catch (e) {
         throw Exception('Failed to reset simulation: $e');
       }
     }
   }
   ```

7. Ejemplo de uso de Reportes de Incidentes en un Widget:

   ```dart
   import 'package:flutter/material.dart';
   import 'package:flutter_sound/flutter_sound.dart';
   import 'dart:io';

   class ReportIncidentScreen extends StatefulWidget {
     @override
     _ReportIncidentScreenState createState() => _ReportIncidentScreenState();
   }

   class _ReportIncidentScreenState extends State<ReportIncidentScreen> {
     final IncidentReportService _service = IncidentReportService();
     final FlutterSoundRecorder _recorder = FlutterSoundRecorder();

     File? _audioFile;
     bool _isRecording = false;
     bool _isLoading = false;

     String _station = 'Observatorio, Línea 1';
     String _type = 'delay';
     String _level = 'medium';
     String _description = '';

     @override
     void initState() {
       super.initState();
       _initRecorder();
     }

     Future<void> _initRecorder() async {
       await _recorder.openRecorder();
     }

     Future<void> _startRecording() async {
       final path = '${Directory.systemTemp.path}/incident_audio.aac';
       await _recorder.startRecorder(toFile: path);
       setState(() {
         _isRecording = true;
       });
     }

     Future<void> _stopRecording() async {
       final path = await _recorder.stopRecorder();
       setState(() {
         _isRecording = false;
         _audioFile = File(path!);
       });
     }

     // Opción 1: Envío automático con IA
     Future<void> _submitAutomaticReport() async {
       if (_audioFile == null) {
         ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Por favor graba un audio primero')),
         );
         return;
       }

       setState(() {
         _isLoading = true;
       });

       try {
         final result = await _service.submitAutomaticReport(
           audioFile: _audioFile!,
         );

         ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Reporte enviado: ${result['message']}')),
         );

         // Mostrar datos extraídos
         showDialog(
           context: context,
           builder: (context) => AlertDialog(
             title: Text('Reporte Procesado'),
             content: Column(
               mainAxisSize: MainAxisSize.min,
               crossAxisAlignment: CrossAxisAlignment.start,
               children: [
                 Text('Estación: ${result['station']}'),
                 Text('Tipo: ${result['type']}'),
                 Text('Nivel: ${result['level']}'),
                 Text('Descripción: ${result['description']}'),
               ],
             ),
             actions: [
               TextButton(
                 onPressed: () => Navigator.pop(context),
                 child: Text('OK'),
               ),
             ],
           ),
         );

         Navigator.pop(context);
       } catch (e) {
         ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Error: $e')),
         );
       } finally {
         setState(() {
           _isLoading = false;
         });
       }
     }

     // Opción 2: Envío manual con formulario
     Future<void> _submitManualReport() async {
       if (_audioFile == null) {
         ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Por favor graba un audio primero')),
         );
         return;
       }

       setState(() {
         _isLoading = true;
       });

       try {
         final result = await _service.submitManualReport(
           audioFile: _audioFile!,
           station: _station,
           type: _type,
           level: _level,
           description: _description.isEmpty ? null : _description,
           incidentDateTime: DateTime.now(),
         );

         ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text(result['message'])),
         );

         Navigator.pop(context);
       } catch (e) {
         ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Error: $e')),
         );
       } finally {
         setState(() {
           _isLoading = false;
         });
       }
     }

     @override
     Widget build(BuildContext context) {
       return Scaffold(
         appBar: AppBar(title: Text('Reportar Incidente')),
         body: Padding(
           padding: EdgeInsets.all(16),
           child: Column(
             children: [
               // Botón de grabación
               ElevatedButton.icon(
                 onPressed: _isRecording ? _stopRecording : _startRecording,
                 icon: Icon(_isRecording ? Icons.stop : Icons.mic),
                 label: Text(_isRecording ? 'Detener Grabación' : 'Grabar Audio'),
                 style: ElevatedButton.styleFrom(
                   backgroundColor: _isRecording ? Colors.red : Colors.blue,
                 ),
               ),

               if (_audioFile != null)
                 Text('✓ Audio grabado'),

               SizedBox(height: 24),

               // Opciones de envío
               Text('Selecciona el tipo de reporte:',
                 style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
               SizedBox(height: 16),

               // Botón para envío automático con IA
               ElevatedButton(
                 onPressed: _isLoading ? null : _submitAutomaticReport,
                 child: _isLoading
                     ? CircularProgressIndicator()
                     : Text('Enviar con Transcripción Automática (IA)'),
               ),

               SizedBox(height: 16),
               Divider(),
               SizedBox(height: 16),

               // Formulario manual
               Text('O llena el formulario manualmente:'),

               DropdownButtonFormField<String>(
                 value: _station,
                 items: [
                   'Observatorio, Línea 1',
                   'Tacubaya, Línea 1',
                   'Juanacatlán, Línea 1',
                   // ... más estaciones
                 ].map((station) {
                   return DropdownMenuItem(value: station, child: Text(station));
                 }).toList(),
                 onChanged: (value) => setState(() => _station = value!),
                 decoration: InputDecoration(labelText: 'Estación'),
               ),

               DropdownButtonFormField<String>(
                 value: _type,
                 items: [
                   {'value': 'delay', 'label': 'Retraso'},
                   {'value': 'incident', 'label': 'Incidente'},
                   {'value': 'maintenance', 'label': 'Mantenimiento'},
                   {'value': 'crowding', 'label': 'Aglomeración'},
                   {'value': 'other', 'label': 'Otro'},
                 ].map((item) {
                   return DropdownMenuItem(
                     value: item['value'],
                     child: Text(item['label']!),
                   );
                 }).toList(),
                 onChanged: (value) => setState(() => _type = value!),
                 decoration: InputDecoration(labelText: 'Tipo de Incidente'),
               ),

               DropdownButtonFormField<String>(
                 value: _level,
                 items: [
                   {'value': 'low', 'label': 'Bajo'},
                   {'value': 'medium', 'label': 'Medio'},
                   {'value': 'high', 'label': 'Alto'},
                   {'value': 'critical', 'label': 'Crítico'},
                 ].map((item) {
                   return DropdownMenuItem(
                     value: item['value'],
                     child: Text(item['label']!),
                   );
                 }).toList(),
                 onChanged: (value) => setState(() => _level = value!),
                 decoration: InputDecoration(labelText: 'Nivel de Severidad'),
               ),

               TextField(
                 onChanged: (value) => _description = value,
                 decoration: InputDecoration(
                   labelText: 'Descripción (opcional)',
                 ),
                 maxLines: 2,
               ),

               SizedBox(height: 16),

               // Botón para envío manual
               ElevatedButton(
                 onPressed: _isLoading ? null : _submitManualReport,
                 child: _isLoading
                     ? CircularProgressIndicator()
                     : Text('Enviar Reporte Manual'),
               ),
             ],
           ),
         ),
       );
     }

     @override
     void dispose() {
       _recorder.closeRecorder();
       super.dispose();
     }
   }
   ```

8. Ejemplo de uso en un Widget:

   ````

   ```dart
   class MetroMapScreen extends StatefulWidget {
     @override
     _MetroMapScreenState createState() => _MetroMapScreenState();
   }

   class _MetroMapScreenState extends State<MetroMapScreen> {
     final MetroService _metroService = MetroService();
     Map<String, dynamic>? _lineStatus;

     @override
     void initState() {
       super.initState();
       _loadInitialData();
       _metroService.startPolling((data) {
         setState(() {
           _lineStatus = data;
         });
       });
     }

     Future<void> _loadInitialData() async {
       final data = await _metroService.getLineStatus();
       setState(() {
         _lineStatus = data;
       });
     }

     @override
     void dispose() {
       _metroService.stopPolling();
       super.dispose();
     }

     @override
     Widget build(BuildContext context) {
       if (_lineStatus == null) {
         return Center(child: CircularProgressIndicator());
       }

       return Scaffold(
         appBar: AppBar(title: Text(_lineStatus!['line_name'])),
         body: Column(
           children: [
             // Mostrar información de la línea
             Card(
               child: Padding(
                 padding: EdgeInsets.all(16),
                 child: Column(
                   children: [
                     Text('Saturación: ${_lineStatus!['saturation']}'),
                     Text('Trenes activos: ${_lineStatus!['active_trains'].length}'),
                     if (_lineStatus!['incident_type'] != 'none')
                       Text('⚠️ ${_lineStatus!['incident_message']}'),
                   ],
                 ),
               ),
             ),
             // Lista de trenes
             Expanded(
               child: ListView.builder(
                 itemCount: _lineStatus!['active_trains'].length,
                 itemBuilder: (context, index) {
                   final train = _lineStatus!['active_trains'][index];
                   return ListTile(
                     title: Text(train['train_id']),
                     subtitle: Text(
                       '${train['current_station']} → ${train['next_station']}'
                     ),
                     trailing: Text(
                       '${(train['progress_to_next'] * 100).toInt()}%'
                     ),
                   );
                 },
               ),
             ),
           ],
         ),
       );
     }
   }
   ````

## Docker

### Iniciar todos los servicios

```bash
docker-compose up -d
```

### Iniciar solo base de datos

```bash
docker-compose up -d postgres
```

### Reconstruir imagen del backend

```bash
docker-compose up -d --build backend
```

### Detener servicios

```bash
docker-compose down
```

### Detener y eliminar volúmenes

```bash
docker-compose down -v
```

### Ver logs

```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo postgres
docker-compose logs -f postgres
```

### Acceder al contenedor del backend

```bash
docker-compose exec backend bash
```

### Acceder a PostgreSQL

```bash
docker-compose exec postgres psql -U postgres -d aihack_db
```

## Comandos Útiles

### Crear migraciones con Alembic (opcional)

```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Ejecutar tests

```bash
pytest
```

### Probar endpoints del metro

```bash
# Ejecutar script de prueba completo
./test_metro_api.sh

# O probar endpoints individuales
curl http://localhost:8000/metro/line1/status | python3 -m json.tool
curl http://localhost:8000/metro/line1/stations | python3 -m json.tool
curl -X POST http://localhost:8000/metro/reset
```

### Probar endpoint de fall detection

```bash
# Ejecutar script de prueba
./test_fall_detection.sh

# O probar manualmente
curl -X POST http://localhost:8000/falldetection \
  -F "image=@ruta/a/imagen.jpg" \
  -F "station=Observatorio" \
  -F "detected_object=persona" \
  -F "incident_datetime=2024-01-20T10:30:00"

# Listar incidentes
curl http://localhost:8000/falldetection | python3 -m json.tool
```

### Probar endpoints de reportes de incidentes con audio

```bash
# Ejecutar script de prueba completo
./test_incident_reports.sh

# O probar manualmente:

# 1. Endpoint manual (audio + formulario)
curl -X POST http://localhost:8000/reports/incident/manual \
  -F "audio=@ruta/a/audio.aac" \
  -F "station=Observatorio, Línea 1" \
  -F "type=delay" \
  -F "level=medium" \
  -F "description=Retraso por falla técnica" \
  -F "incident_datetime=2024-01-20T14:30:00.000Z"

# 2. Endpoint automático (solo audio + IA)
# Requiere OPENAI_API_KEY configurada
curl -X POST http://localhost:8000/reports/incident/automatic \
  -F "audio=@ruta/a/audio.aac"

# 3. Listar reportes
curl http://localhost:8000/reports/incident/ | python3 -m json.tool

# 4. Obtener reporte específico
curl http://localhost:8000/reports/incident/1 | python3 -m json.tool

# 5. Eliminar reporte
curl -X DELETE http://localhost:8000/reports/incident/1
```

## Seguridad

- Las contraseñas se hashean con bcrypt
- Los tokens JWT tienen expiración configurable
- Las rutas protegidas requieren token válido
- CORS configurado (ajustar para producción)

## Producción

Para desplegar en producción:

1. Cambiar `SECRET_KEY` en `.env`
2. Configurar CORS con orígenes específicos
3. Usar base de datos externa (no Docker local)
4. Configurar HTTPS
5. Usar servidor ASGI como Gunicorn con Uvicorn workers

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Licencia

MIT
