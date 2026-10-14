from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from backend.app.core.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(String, unique=True, nullable=False, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String)
    file_type = Column(String)
    file_size = Column(Integer)
    sha256_hash = Column(String)
    status = Column(String, default="SUBMITTED")
    created_at = Column(DateTime, default=datetime.utcnow)