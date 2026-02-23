from app.config import settings
from app.models import RecommendationPublishRun, RecommendationPublishState


class RecommendationPublishRepository:
    def __init__(self, db):
        self.db = db

    def get_state(self, placement):
        return (
            self.db.query(RecommendationPublishState)
            .filter(RecommendationPublishState.placement == placement)
            .first()
        )

    def update_publish_state(self, placement, current_version, previous_version):
        try:
            state = (
                self.db.query(RecommendationPublishState)
                .filter(RecommendationPublishState.placement == placement)
                .first()
            )
            if state:
                state.current_version = current_version
                state.previous_version = previous_version
            else:
                state = RecommendationPublishState(
                    placement=placement,
                    current_version=current_version,
                    previous_version=previous_version,
                )
                self.db.add(state)
            self.db.commit()
            self.db.refresh(state)
            return state
        except Exception:
            self.db.rollback()
            settings.logger.exception("Error updating recommendation publish state")
            raise

    def create_run(self, run_date, status, product_count, order_count, message=None):
        try:
            run = RecommendationPublishRun(
                run_date=run_date,
                status=status,
                product_count=product_count,
                order_count=order_count,
                message=message,
            )
            self.db.add(run)
            self.db.commit()
            self.db.refresh(run)
            return run
        except Exception:
            self.db.rollback()
            settings.logger.exception("Error creating recommendation publish run")
            raise

    def get_latest_run(self):
        return (
            self.db.query(RecommendationPublishRun)
            .order_by(
                RecommendationPublishRun.run_date.desc(),
                RecommendationPublishRun.id.desc(),
            )
            .first()
        )

    def get_run_for_date(self, run_date):
        return (
            self.db.query(RecommendationPublishRun)
            .filter(RecommendationPublishRun.run_date == run_date)
            .order_by(RecommendationPublishRun.id.desc())
            .first()
        )
