from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum

class IncidentType(str, enum.Enum):
    delay = "delay"
    incident = "incident"
    maintenance = "maintenance"
    crowding = "crowding"
    other = "other"

class IncidentLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id = Column(Integer, primary_key=True, index=True)
    audio_url = Column(String, nullable=False)
    station = Column(String, nullable=False)
    type = Column(SQLEnum(IncidentType), nullable=False)
    level = Column(SQLEnum(IncidentLevel), nullable=False)
    description = Column(Text, nullable=True)
    incident_datetime = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
