from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from backend.app.core.database import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id = Column(Integer, primary_key=True, index=True)

    evidence_id = Column(
        String,
        nullable=False,
        index=True
    )

    evidence_hash = Column(
        String,
        nullable=False
    )

    evidence_type = Column(String)

    summary = Column(Text)

    key_entities = Column(Text)

    important_dates = Column(Text)

    locations = Column(Text)

    important_observations = Column(Text)

    potentially_relevant_information = Column(Text)

    confidence_level = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )