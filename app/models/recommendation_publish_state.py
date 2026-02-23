from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from .base import Base


class RecommendationPublishState(Base):
    __tablename__ = "recommendation_publish_state"

    id = Column(Integer, primary_key=True, index=True)
    placement = Column(String(50), index=True, nullable=False)
    current_version = Column(Integer, nullable=False)
    previous_version = Column(Integer, nullable=True)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
