from fastapi import APIRouter
from typing import List
from app.schemas.metro import LineStatus, Station, SimulationReset
from app.utils.metro_simulator import metro_simulator, metro_simulator_line2

router = APIRouter(prefix="/metro", tags=["Metro"])

# ==================== LÍNEA 1 ====================

@router.get("/line1/status", response_model=LineStatus)
async def get_line1_status():
    """
    Obtiene el estado en tiempo real de la Línea 1 del Metro
    
    Incluye:
    - Estado general de la línea (saturación, incidentes)
    - Posición y datos de todos los trenes activos
    - Ocupación de vagones
    """
    return metro_simulator.get_line_status()

@router.get("/line1/stations", response_model=List[Station])
async def get_line1_stations():
    """
    Obtiene el estado de todas las estaciones de la Línea 1
    
    Incluye:
    - Información de ubicación
    - Nivel de saturación
    - Tiempo de espera estimado
    - Personas esperando
    - Tiempo hasta próximo tren
    """
    return metro_simulator.get_stations()

# ==================== LÍNEA 2 ====================

@router.get("/line2/status", response_model=LineStatus)
async def get_line2_status():
    """
    Obtiene el estado en tiempo real de la Línea 2 del Metro (Azul)
    
    Incluye:
    - Estado general de la línea (saturación, incidentes)
    - Posición y datos de todos los trenes activos
    - Ocupación de vagones
    """
    return metro_simulator_line2.get_line_status()

@router.get("/line2/stations", response_model=List[Station])
async def get_line2_stations():
    """
    Obtiene el estado de todas las estaciones de la Línea 2 (Azul)
    
    Incluye:
    - Información de ubicación
    - Nivel de saturación
    - Tiempo de espera estimado
    - Personas esperando
    - Tiempo hasta próximo tren
    """
    return metro_simulator_line2.get_stations()

# ==================== RESET ====================

@router.post("/reset", response_model=SimulationReset)
async def reset_simulation():
    """
    Reinicia la simulación del metro a su estado inicial
    
    Reinicia AMBAS líneas (Línea 1 y Línea 2)
    
    Útil para:
    - Resetear la simulación durante pruebas
    - Limpiar incidentes
    - Redistribuir trenes
    """
    metro_simulator.reset()
    metro_simulator_line2.reset()
    return {"message": "Simulación de ambas líneas reiniciada exitosamente", "timestamp": metro_simulator.last_updated}
