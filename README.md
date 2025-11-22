# AIHack Backend

Backend API desarrollado con FastAPI para aplicación Flutter, con autenticación JWT y PostgreSQL.

## Características

- 🔐 Autenticación JWT
- 🐘 Base de datos PostgreSQL con Docker
- 🚀 FastAPI con soporte async
- 🔒 Hash de contraseñas con bcrypt
- ✅ Validación de datos con Pydantic
- 🌐 CORS configurado para Flutter

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
