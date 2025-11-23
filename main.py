from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
from pathlib import Path
from app.database import engine, Base
from app.routes import auth_router, metro_router, fall_detection_router, incident_reports_router
from app.utils.metro_simulator import metro_simulator

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación"""
    # Startup: Crear tablas y iniciar simulación
    Base.metadata.create_all(bind=engine)
    
    # Crear directorio de storage para audios
    Path("storage/incidents").mkdir(parents=True, exist_ok=True)
    
    # Iniciar simulación del metro en background
    simulation_task = asyncio.create_task(metro_simulator.update_loop())
    
    yield
    
    # Shutdown: Detener simulación
    metro_simulator.stop()
    simulation_task.cancel()
    try:
        await simulation_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="AIHack Backend API",
    description="Backend API with JWT authentication, real-time metro simulation, and fall detection for Flutter app",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(metro_router)
app.include_router(fall_detection_router)
app.include_router(incident_reports_router)

# Mount static files for audio storage
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

@app.get("/")
async def root():
    return {
        "message": "AIHack Backend API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
