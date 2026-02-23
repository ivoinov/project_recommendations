from sqlalchemy import Column, Date, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from .base import Base


class RecommendationPublishRun(Base):
    __tablename__ = "recommendation_publish_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)
    product_count = Column(Integer, nullable=True)
    order_count = Column(Integer, nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
