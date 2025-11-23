#!/bin/bash

echo "=============================================="
echo "  Guía: Hacer POST a /falldetection"
echo "=============================================="
echo ""

# Verificar que existe una imagen
if [ ! -f "/tmp/test_fall_detection.jpg" ]; then
    echo "Creando imagen de prueba..."
    python3 -c "
from PIL import Image
img = Image.new('RGB', (100, 100), color='blue')
img.save('/tmp/test_fall_detection.jpg')
"
    echo "✓ Imagen creada"
    echo ""
fi

# Obtener fecha/hora actual en formato ISO
CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S")

echo "📋 EJEMPLO 1: POST con curl"
echo "────────────────────────────────────────────"
echo ""
echo "curl -X POST http://localhost:8000/falldetection \\"
echo "  -F \"image=@/tmp/test_fall_detection.jpg\" \\"
echo "  -F \"station=Observatorio\" \\"
echo "  -F \"detected_object=persona\" \\"
echo "  -F \"incident_datetime=$CURRENT_TIME\""
echo ""
echo ""

echo "📋 EJEMPLO 2: POST con diferentes estaciones"
echo "────────────────────────────────────────────"
echo ""
echo "# Tacubaya"
echo "curl -X POST http://localhost:8000/falldetection \\"
echo "  -F \"image=@imagen.jpg\" \\"
echo "  -F \"station=Tacubaya\" \\"
echo "  -F \"detected_object=bicicleta\" \\"
echo "  -F \"incident_datetime=$(date -u +"%Y-%m-%dT%H:%M:%S")\""
echo ""
echo "# Juanacatlán"
echo "curl -X POST http://localhost:8000/falldetection \\"
echo "  -F \"image=@imagen.jpg\" \\"
echo "  -F \"station=Juanacatlán\" \\"
echo "  -F \"detected_object=maleta\" \\"
echo "  -F \"incident_datetime=$(date -u +"%Y-%m-%dT%H:%M:%S")\""
echo ""
echo ""

echo "📋 EJEMPLO 3: POST desde Python"
echo "────────────────────────────────────────────"
cat << 'EOF'

import requests
from datetime import datetime

url = "http://localhost:8000/falldetection"

# Preparar datos
files = {
    'image': open('/tmp/test_fall_detection.jpg', 'rb')
}

data = {
    'station': 'Observatorio',
    'detected_object': 'persona',
    'incident_datetime': datetime.utcnow().isoformat()
}

# Hacer POST
response = requests.post(url, files=files, data=data)
print(response.json())

EOF
echo ""
echo ""

echo "📋 EJEMPLO 4: Formato de fecha/hora"
echo "────────────────────────────────────────────"
echo ""
echo "Formatos válidos ISO 8601:"
echo "  • $CURRENT_TIME"
echo "  • ${CURRENT_TIME}Z"
echo "  • ${CURRENT_TIME}+00:00"
echo "  • 2024-01-20T10:30:00"
echo ""
echo ""

echo "📋 EJEMPLO 5: Objetos detectados válidos"
echo "────────────────────────────────────────────"
echo ""
echo "  • persona"
echo "  • bicicleta"
echo "  • maleta"
echo "  • silla_ruedas"
echo "  • carrito"
echo "  • otro"
echo ""
echo ""

echo "⚠️  NOTA IMPORTANTE: AWS S3"
echo "────────────────────────────────────────────"
echo ""
echo "Para que el POST funcione, necesitas configurar"
echo "las credenciales de AWS S3 en .env:"
echo ""
echo "  AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX"
echo "  AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxx"
echo "  AWS_REGION=us-east-1"
echo "  AWS_S3_BUCKET=aihack-fall-detection"
echo ""
echo "Luego reinicia el backend:"
echo "  docker-compose restart backend"
echo ""
echo ""

echo "📝 PROBAR AHORA (requiere AWS configurado):"
echo "────────────────────────────────────────────"
echo ""
read -p "¿Hacer POST de prueba? (s/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]
then
    echo ""
    echo "Enviando POST..."
    echo ""
    
    curl -X POST http://localhost:8000/falldetection \
      -F "image=@/tmp/test_fall_detection.jpg" \
      -F "station=Observatorio" \
      -F "detected_object=persona" \
      -F "incident_datetime=$CURRENT_TIME" \
      -w "\n\nHTTP Status: %{http_code}\n" | python3 -m json.tool 2>&1 || echo ""
    
    echo ""
fi

echo ""
echo "=============================================="
echo "  Ver documentación interactiva:"
echo "  http://localhost:8000/docs#/Fall%20Detection/create_fall_detection_falldetection_post"
echo "=============================================="
