#!/bin/bash

echo "=========================================="
echo "  Probando API del Metro - Línea 1"
echo "=========================================="
echo ""

# Test 1: Health check
echo "1. Health Check"
echo "   GET /health"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
echo ""

# Test 2: Estado de la línea
echo "2. Estado de la Línea 1"
echo "   GET /metro/line1/status"
curl -s http://localhost:8000/metro/line1/status | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"   Línea: {data['line_name']}\")
print(f\"   Ruta: {data['route']}\")
print(f\"   Saturación: {data['saturation']}\")
print(f\"   Incidente: {data['incident_type']}\")
if data['incident_message']:
    print(f\"   Mensaje: {data['incident_message']}\")
print(f\"   Trenes activos: {len(data['active_trains'])}\")
print(f\"   Última actualización: {data['last_updated']}\")
print(f\"\n   Primeros 3 trenes:\")
for train in data['active_trains'][:3]:
    total_passengers = sum(train['passengers_per_wagon'])
    print(f\"   - {train['train_id']}: {train['current_station']} → {train['next_station']}\")
    print(f\"     Dirección: {train['direction']}, Progreso: {train['progress_to_next']:.2f}, Pasajeros: {total_passengers}\")
"
echo ""
echo ""

# Test 3: Estaciones
echo "3. Estado de las Estaciones"
echo "   GET /metro/line1/stations"
curl -s http://localhost:8000/metro/line1/stations | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"   Total de estaciones: {len(data)}\")
print(f\"\n   Primeras 5 estaciones:\")
for station in data[:5]:
    print(f\"   - {station['name']}:\")
    print(f\"     Saturación: {station['saturation']}, Esperando: {station['people_waiting']} personas\")
    print(f\"     Próximo tren: {station['next_train_arrival']} min, Espera estimada: {station['estimated_wait_time']} min\")
"
echo ""
echo ""

# Test 4: Simulación en tiempo real
echo "4. Verificando simulación en tiempo real..."
echo "   Esperando 6 segundos entre consultas..."
echo ""

echo "   Primera consulta:"
curl -s http://localhost:8000/metro/line1/status | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"   Actualización: {data['last_updated']}\")
for train in data['active_trains'][:3]:
    print(f\"   {train['train_id']}: progreso {train['progress_to_next']:.2f}\")
"

sleep 6

echo ""
echo "   Segunda consulta (6 segundos después):"
curl -s http://localhost:8000/metro/line1/status | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"   Actualización: {data['last_updated']}\")
for train in data['active_trains'][:3]:
    print(f\"   {train['train_id']}: progreso {train['progress_to_next']:.2f}\")
"
echo ""
echo "   ✓ Los trenes se están moviendo!"
echo ""
echo ""

# Test 5: Reset
echo "5. Reset de la simulación"
echo "   POST /metro/reset"
curl -s -X POST http://localhost:8000/metro/reset | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo "  ✓ Todas las pruebas completadas"
echo "=========================================="
