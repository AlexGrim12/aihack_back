# AIHack Backend

Backend API desarrollado con FastAPI para aplicación Flutter, con autenticación JWT y PostgreSQL.

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

## Requisitos

- Python 3.9+
- Docker y Docker Compose
- pip

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

3. Ejemplo de servicio del Metro en Flutter:

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

4. Ejemplo de uso en un Widget:

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
   ```

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
