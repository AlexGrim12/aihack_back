from app.routes.auth import router as auth_router
from app.routes.metro import router as metro_router
from app.routes.fall_detection import router as fall_detection_router

__all__ = ["auth_router", "metro_router", "fall_detection_router"]
