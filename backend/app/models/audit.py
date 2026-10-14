from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from backend.app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)
    result = Column(String, nullable=False)
    original_hash = Column(String)
    current_hash = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    previous_hash = Column(String)
    event_hash = Column(String, index=True)