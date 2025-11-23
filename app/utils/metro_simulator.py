import random
import asyncio
from datetime import datetime
from typing import List, Dict, Literal
from app.schemas.metro import Train, Station, LineStatus

# Configuración de estaciones de la Línea 1
STATIONS = [
    {"id": "observatorio", "name": "Observatorio", "lat": 19.3986, "lng": -99.2009},
    {"id": "tacubaya", "name": "Tacubaya", "lat": 19.4033, "lng": -99.1876},
    {"id": "juanacatlan", "name": "Juanacatlán", "lat": 19.4121, "lng": -99.1826},
    {"id": "chapultepec", "name": "Chapultepec", "lat": 19.4206, "lng": -99.1676},
    {"id": "sevilla", "name": "Sevilla", "lat": 19.4218, "lng": -99.1607},
    {"id": "insurgentes", "name": "Insurgentes", "lat": 19.4237, "lng": -99.1628},
    {"id": "cuauhtemoc", "name": "Cuauhtémoc", "lat": 19.4254, "lng": -99.1547},
    {"id": "balderas", "name": "Balderas", "lat": 19.4272, "lng": -99.1495},
    {"id": "salto_del_agua", "name": "Salto del Agua", "lat": 19.4274, "lng": -99.1428},
    {"id": "isabel_la_catolica", "name": "Isabel la Católica", "lat": 19.4261, "lng": -99.1379},
    {"id": "pino_suarez", "name": "Pino Suárez", "lat": 19.4257, "lng": -99.1330},
    {"id": "merced", "name": "Merced", "lat": 19.4254, "lng": -99.1201},
    {"id": "candelaria", "name": "Candelaria", "lat": 19.4290, "lng": -99.1153},
    {"id": "san_lazaro", "name": "San Lázaro", "lat": 19.4306, "lng": -99.1154},
    {"id": "moctezuma", "name": "Moctezuma", "lat": 19.4277, "lng": -99.1126},
    {"id": "balbuena", "name": "Balbuena", "lat": 19.4234, "lng": -99.1013},
    {"id": "boulevard_puerto_aereo", "name": "Boulevard Puerto Aéreo", "lat": 19.4195, "lng": -99.0962},
    {"id": "gomez_farias", "name": "Gómez Farías", "lat": 19.4162, "lng": -99.0903},
    {"id": "zaragoza", "name": "Zaragoza", "lat": 19.4122, "lng": -99.0825},
    {"id": "pantitlan", "name": "Pantitlán", "lat": 19.4153, "lng": -99.0733}
]

INCIDENT_MESSAGES = {
    "delay": [
        "Retraso de 5 minutos por afluencia",
        "Demora temporal por alta demanda de usuarios",
        "Servicio lento por sobrecupo en estaciones"
    ],
    "incident": [
        "Revisión técnica en progreso",
        "Atención de usuario en andén",
        "Inspección de vías en curso"
    ],
    "maintenance": [
        "Mantenimiento programado en estación",
        "Trabajos de mantenimiento preventivo",
        "Revisión de sistemas de señalización"
    ]
}

class MetroSimulator:
    def __init__(self):
        self.trains: List[Dict] = []
        self.stations_data: List[Dict] = []
        self.incident_type: Literal["none", "delay", "incident", "maintenance"] = "none"
        self.incident_message: str = None
        self.last_updated = datetime.now()
        self.is_running = False
        self._initialize_simulation()
    
    def _initialize_simulation(self):
        """Inicializa la simulación con trenes y estaciones"""
        # Crear 7 trenes iniciales
        num_trains = 7
        for i in range(num_trains):
            # Distribuir trenes uniformemente en la línea
            station_index = int((len(STATIONS) - 1) * i / num_trains)
            current_station = STATIONS[station_index]
            
            # Alternar direcciones
            if i % 2 == 0:
                direction = "Pantitlán"
                next_station_index = min(station_index + 1, len(STATIONS) - 1)
            else:
                direction = "Observatorio"
                next_station_index = max(station_index - 1, 0)
            
            next_station = STATIONS[next_station_index]
            
            train = {
                "train_id": f"T10{i+1}",
                "current_station_index": station_index,
                "next_station_index": next_station_index,
                "current_station": current_station["name"],
                "next_station": next_station["name"],
                "direction": direction,
                "progress_to_next": random.uniform(0.0, 0.8),
                "speed": random.uniform(0.015, 0.025)  # Velocidad de progreso por tick
            }
            self.trains.append(train)
        
        # Inicializar datos de estaciones
        self._update_stations_data()
        
        # 10% probabilidad de incidente inicial
        if random.random() < 0.1:
            self._generate_incident()
    
    def _generate_incident(self):
        """Genera un incidente aleatorio"""
        incident_types = ["delay", "incident", "maintenance"]
        self.incident_type = random.choice(incident_types)
        self.incident_message = random.choice(INCIDENT_MESSAGES[self.incident_type])
    
    def _clear_incident(self):
        """Limpia el incidente actual"""
        self.incident_type = "none"
        self.incident_message = None
    
    def _update_trains(self):
        """Actualiza la posición de todos los trenes"""
        for train in self.trains:
            # Incrementar progreso
            train["progress_to_next"] += train["speed"]
            
            # Si llegó a la siguiente estación
            if train["progress_to_next"] >= 1.0:
                train["progress_to_next"] = 0.0
                train["current_station_index"] = train["next_station_index"]
                
                # Determinar siguiente estación según dirección
                if train["direction"] == "Pantitlán":
                    if train["current_station_index"] >= len(STATIONS) - 1:
                        # Cambiar dirección en terminal
                        train["direction"] = "Observatorio"
                        train["next_station_index"] = train["current_station_index"] - 1
                    else:
                        train["next_station_index"] = train["current_station_index"] + 1
                else:  # Observatorio
                    if train["current_station_index"] <= 0:
                        # Cambiar dirección en terminal
                        train["direction"] = "Pantitlán"
                        train["next_station_index"] = train["current_station_index"] + 1
                    else:
                        train["next_station_index"] = train["current_station_index"] - 1
                
                # Actualizar nombres de estaciones
                train["current_station"] = STATIONS[train["current_station_index"]]["name"]
                train["next_station"] = STATIONS[train["next_station_index"]]["name"]
                
                # Nueva velocidad aleatoria
                train["speed"] = random.uniform(0.015, 0.025)
        
        # Manejar incidentes (10% probabilidad de cambio)
        if random.random() < 0.1:
            if self.incident_type == "none":
                self._generate_incident()
            else:
                self._clear_incident()
        
        self.last_updated = datetime.now()
    
    def _calculate_saturation(self, people: int) -> Literal["low", "medium", "high", "full"]:
        """Calcula el nivel de saturación basado en cantidad de personas"""
        if people < 30:
            return "low"
        elif people < 50:
            return "medium"
        elif people < 70:
            return "high"
        else:
            return "full"
    
    def _update_stations_data(self):
        """Actualiza los datos de todas las estaciones"""
        self.stations_data = []
        
        for i, station_info in enumerate(STATIONS):
            # Buscar trenes cercanos a esta estación
            trains_near = []
            for train in self.trains:
                if train["next_station_index"] == i:
                    # Calcular tiempo estimado de llegada (en minutos)
                    remaining_progress = 1.0 - train["progress_to_next"]
                    eta_minutes = int((remaining_progress / train["speed"]) * 3 / 60) + 1
                    trains_near.append(eta_minutes)
            
            # Tiempo hasta próximo tren
            next_train_arrival = min(trains_near) if trains_near else random.randint(5, 10)
            
            # Personas esperando (más en horas pico simuladas)
            people_waiting = random.randint(20, 100)
            
            station_data = {
                "id": station_info["id"],
                "name": station_info["name"],
                "latitude": station_info["lat"],
                "longitude": station_info["lng"],
                "saturation": self._calculate_saturation(people_waiting),
                "estimated_wait_time": random.randint(2, 5),
                "has_incident": False,
                "incident_message": None,
                "people_waiting": people_waiting,
                "next_train_arrival": next_train_arrival
            }
            
            self.stations_data.append(station_data)
    
    async def update_loop(self):
        """Loop principal de actualización (ejecutar en background)"""
        self.is_running = True
        while self.is_running:
            await asyncio.sleep(3)
            self._update_trains()
            self._update_stations_data()
    
    def get_line_status(self) -> LineStatus:
        """Obtiene el estado actual de la línea"""
        # Calcular saturación general
        avg_passengers = sum(
            sum(random.randint(20, 60) for _ in range(6)) 
            for _ in self.trains
        ) / len(self.trains) / 6
        
        if avg_passengers < 35:
            saturation = "low"
        elif avg_passengers < 50:
            saturation = "medium"
        elif avg_passengers < 65:
            saturation = "high"
        else:
            saturation = "full"
        
        # Convertir trenes a formato de respuesta
        active_trains = []
        for train in self.trains:
            passengers = [random.randint(20, 60) for _ in range(6)]
            
            train_data = Train(
                train_id=train["train_id"],
                current_station=train["current_station"],
                next_station=train["next_station"],
                direction=train["direction"],
                progress_to_next=round(train["progress_to_next"], 2),
                wagons=6,
                passengers_per_wagon=passengers
            )
            active_trains.append(train_data)
        
        return LineStatus(
            line_name="Línea 1",
            route="Observatorio ↔ Pantitlán",
            saturation=saturation,
            incident_type=self.incident_type,
            incident_message=self.incident_message,
            last_updated=self.last_updated,
            active_trains=active_trains
        )
    
    def get_stations(self) -> List[Station]:
        """Obtiene el estado de todas las estaciones"""
        return [Station(**station) for station in self.stations_data]
    
    def reset(self):
        """Reinicia la simulación"""
        self.trains.clear()
        self.stations_data.clear()
        self._clear_incident()
        self._initialize_simulation()
        return {"message": "Simulación reiniciada exitosamente", "timestamp": datetime.now()}
    
    def stop(self):
        """Detiene el loop de simulación"""
        self.is_running = False

# Instancia global del simulador
metro_simulator = MetroSimulator()
