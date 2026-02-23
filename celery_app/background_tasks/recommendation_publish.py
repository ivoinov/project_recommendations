from datetime import datetime, timezone

from app.config import db_settings, settings
from app.services.recommendation_publish_service import publish_shop_candidates
from app.services.shop_db import list_shop_ids


def run_daily_publish():
    run_date = datetime.now(timezone.utc).date()
    db_generator = db_settings.get_db()
    db = next(db_generator)
    try:
        shop_ids = list_shop_ids(db)
    finally:
        db_generator.close()

    if not shop_ids:
        settings.logger.info("Daily publish skipped: no shop schemas found")
        return {
            "run_date": str(run_date),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "results": [],
        }

    results = []
    success_count = 0
    failed_count = 0
    skipped_count = 0
    for shop_id in shop_ids:
        result = publish_shop_candidates(shop_id, run_date=run_date)
        status = result.get("status")
        if status == "success":
            success_count += 1
        elif status == "failed":
            failed_count += 1
        else:
            skipped_count += 1
        results.append(
            {
                "shop_id": shop_id,
                "status": status,
                "message": result.get("message"),
            }
        )

    settings.logger.info(
        "Daily publish completed: %s success, %s failed, %s skipped",
        success_count,
        failed_count,
        skipped_count,
    )
    return {
        "run_date": str(run_date),
        "success": success_count,
        "failed": failed_count,
        "skipped": skipped_count,
        "results": results,
    }
