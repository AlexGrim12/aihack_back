#!/bin/bash

echo "=========================================="
echo "  Probando API Fall Detection"
echo "=========================================="
echo ""

# Crear una imagen de prueba temporal
echo "1. Creando imagen de prueba..."
cat > /tmp/test_image.txt << 'EOF'
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==
EOF

# Decodificar base64 a imagen real
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" | base64 -d > /tmp/test_image.png

echo "✓ Imagen de prueba creada"
echo ""

# Test 1: Health check
echo "2. Health Check"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
echo ""

# Test 2: Crear incidente de fall detection
echo "3. Crear incidente de fall detection"
echo "   POST /falldetection"
echo ""

CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S")

echo "   Enviando datos:"
echo "   - Estación: Observatorio"
echo "   - Objeto: persona"
echo "   - Fecha/Hora: $CURRENT_TIME"
echo ""

RESPONSE=$(curl -s -X POST http://localhost:8000/falldetection \
  -F "image=@/tmp/test_image.png" \
  -F "station=Observatorio" \
  -F "detected_object=persona" \
  -F "incident_datetime=$CURRENT_TIME")

echo "$RESPONSE" | python3 -m json.tool

# Extraer ID del incidente creado
INCIDENT_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['fall_detection']['id'])" 2>/dev/null)

echo ""
echo ""

# Test 3: Obtener todos los incidentes
echo "4. Obtener todos los incidentes"
echo "   GET /falldetection"
echo ""

curl -s http://localhost:8000/falldetection | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'   Total de incidentes: {len(data)}')
print('')
for incident in data[:3]:
    print(f\"   ID: {incident['id']}\")
    print(f\"   Estación: {incident['station']}\")
    print(f\"   Objeto: {incident['detected_object']}\")
    print(f\"   Fecha: {incident['incident_datetime']}\")
    print(f\"   Imagen: {incident['image_url'][:60]}...\")
    print('')
"

echo ""

# Test 4: Obtener incidente específico (si se creó)
if [ ! -z "$INCIDENT_ID" ]; then
    echo "5. Obtener incidente específico"
    echo "   GET /falldetection/$INCIDENT_ID"
    echo ""
    
    curl -s http://localhost:8000/falldetection/$INCIDENT_ID | python3 -m json.tool
    echo ""
fi

echo ""
echo "=========================================="
echo "  ✓ Pruebas completadas"
echo "=========================================="
echo ""
echo "Nota: Si ves errores de S3, asegúrate de configurar"
echo "las credenciales de AWS en el archivo .env:"
echo ""
echo "  AWS_ACCESS_KEY_ID=tu-access-key"
echo "  AWS_SECRET_ACCESS_KEY=tu-secret-key"
echo "  AWS_REGION=tu-region"
echo "  AWS_S3_BUCKET=tu-bucket"
echo ""

# Limpiar
rm -f /tmp/test_image.png /tmp/test_image.txt
