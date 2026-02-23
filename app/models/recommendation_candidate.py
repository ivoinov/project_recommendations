from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from .base import Base


class RecommendationCandidate(Base):
    __tablename__ = "recommendation_candidates"

    id = Column(Integer, primary_key=True, index=True)
    seed_sku = Column(String(255), index=True, nullable=False)
    placement = Column(String(50), index=True, nullable=False)
    candidate_type = Column(String(50), index=True, nullable=False)
    candidate_sku = Column(String(255), nullable=False)
    score = Column(Float, nullable=False)
    version = Column(Integer, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
