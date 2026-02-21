from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from .base import Base


class RecommendationEvent(Base):
    __tablename__ = "recommendation_events"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    placement = Column(String(50), index=True)
    event_type = Column(String(50), index=True)
    context_skus = Column(Text)
    recommended_sku = Column(String(255))
    session_id = Column(String(255), nullable=True)
    customer_id = Column(Integer, nullable=True)
    request_id = Column(String(255), nullable=True)
