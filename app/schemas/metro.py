from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class Train(BaseModel):
    train_id: str
    current_station: str
    next_station: str
    direction: Literal["Pantitlán", "Observatorio"]
    progress_to_next: float = Field(ge=0.0, le=1.0, description="Progreso hacia siguiente estación (0.0 a 1.0)")
    wagons: int = 6
    passengers_per_wagon: List[int] = Field(default_factory=list, description="Pasajeros por vagón")

class LineStatus(BaseModel):
    line_name: str = "Línea 1"
    route: str = "Observatorio ↔ Pantitlán"
    saturation: Literal["low", "medium", "high", "full"]
    incident_type: Literal["none", "delay", "incident", "maintenance"]
    incident_message: Optional[str] = None
    last_updated: datetime
    active_trains: List[Train]

class Station(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    saturation: Literal["low", "medium", "high", "full"]
    estimated_wait_time: int = Field(description="Tiempo estimado de espera en minutos")
    has_incident: bool = False
    incident_message: Optional[str] = None
    people_waiting: int = Field(ge=0, description="Personas esperando en la estación")
    next_train_arrival: int = Field(description="Minutos hasta el próximo tren")

class SimulationReset(BaseModel):
    message: str
    timestamp: datetime
