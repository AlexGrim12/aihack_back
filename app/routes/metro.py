from fastapi import APIRouter
from typing import List
from app.schemas.metro import LineStatus, Station, SimulationReset
from app.utils.metro_simulator import metro_simulator

router = APIRouter(prefix="/metro", tags=["Metro"])

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

@router.post("/reset", response_model=SimulationReset)
async def reset_simulation():
    """
    Reinicia la simulación del metro a su estado inicial
    
    Útil para:
    - Resetear la simulación durante pruebas
    - Limpiar incidentes
    - Redistribuir trenes
    """
    return metro_simulator.reset()
