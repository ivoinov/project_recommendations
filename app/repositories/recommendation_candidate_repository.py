from app.config import settings
from app.models import RecommendationCandidate


class RecommendationCandidateRepository:
    def __init__(self, db):
        self.db = db

    def create_candidates(
        self, seed_sku, placement, candidate_type, version, candidates_with_scores
    ):
        if not candidates_with_scores:
            return []
        try:
            candidates = [
                RecommendationCandidate(
                    seed_sku=seed_sku,
                    placement=placement,
                    candidate_type=candidate_type,
                    candidate_sku=candidate_sku,
                    score=score,
                    version=version,
                )
                for candidate_sku, score in candidates_with_scores
            ]
            self.db.add_all(candidates)
            self.db.commit()
            return candidates
        except Exception:
            self.db.rollback()
            settings.logger.exception("Error creating recommendation candidates")
            raise

    def get_candidates(self, seed_sku, placement, candidate_type, version, limit=None):
        query = (
            self.db.query(RecommendationCandidate)
            .filter(RecommendationCandidate.seed_sku == seed_sku)
            .filter(RecommendationCandidate.placement == placement)
            .filter(RecommendationCandidate.candidate_type == candidate_type)
            .filter(RecommendationCandidate.version == version)
            .order_by(
                RecommendationCandidate.score.desc(),
                RecommendationCandidate.candidate_sku.asc(),
            )
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    def delete_versions_older_than(self, placement, keep_versions=2):
        try:
            versions = (
                self.db.query(RecommendationCandidate.version)
                .filter(RecommendationCandidate.placement == placement)
                .distinct()
                .order_by(RecommendationCandidate.version.desc())
                .all()
            )
            version_values = [version for (version,) in versions]
            if len(version_values) <= keep_versions:
                return 0
            versions_to_delete = version_values[keep_versions:]
            deleted = (
                self.db.query(RecommendationCandidate)
                .filter(RecommendationCandidate.placement == placement)
                .filter(RecommendationCandidate.version.in_(versions_to_delete))
                .delete(synchronize_session=False)
            )
            self.db.commit()
            return deleted
        except Exception:
            self.db.rollback()
            settings.logger.exception(
                "Error deleting old recommendation candidate versions"
            )
            raise
