from sqlalchemy import func

from app.config import settings
from app.models import RecommendationEvent


class RecommendationEventRepository:
    def __init__(self, db):
        self.db = db

    def create(self, event: RecommendationEvent) -> RecommendationEvent:
        try:
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            return event
        except Exception:
            self.db.rollback()
            settings.logger.exception("Error creating recommendation event")
            raise

    def count_by_placement_and_type(self, from_ts, to_ts, placement=None):
        try:
            query = (
                self.db.query(
                    RecommendationEvent.placement,
                    RecommendationEvent.event_type,
                    func.count(RecommendationEvent.id).label("count"),
                )
                .filter(RecommendationEvent.created_at >= from_ts)
                .filter(RecommendationEvent.created_at <= to_ts)
            )
            if placement:
                query = query.filter(RecommendationEvent.placement == placement)
            rows = (
                query.group_by(
                    RecommendationEvent.placement, RecommendationEvent.event_type
                )
                .order_by(
                    RecommendationEvent.placement.asc(),
                    RecommendationEvent.event_type.asc(),
                )
                .all()
            )
            return [
                {
                    "placement": row.placement,
                    "event_type": row.event_type,
                    "count": row.count,
                }
                for row in rows
            ]
        except Exception:
            self.db.rollback()
            settings.logger.exception("Error aggregating recommendation events")
            raise
