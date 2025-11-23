from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class FallDetection(Base):
    __tablename__ = "fall_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    station = Column(String, nullable=False)
    detected_object = Column(String, nullable=False)
    incident_datetime = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
