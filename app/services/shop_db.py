import re

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import db_settings, settings
from app.models.base import Base

SHOP_ID_PATTERN = re.compile(r"^[a-z0-9_]+$")


def normalize_shop_id(shop_id: str) -> str:
    if shop_id is None:
        raise ValueError("shop_id is required")
    normalized = shop_id.strip().lower()
    if not normalized or not SHOP_ID_PATTERN.match(normalized):
        raise ValueError("shop_id must be lowercase alphanumeric with underscores only")
    return normalized


def shop_schema_name(shop_id: str) -> str:
    normalized = normalize_shop_id(shop_id)
    return f"shop_{normalized}"


def ensure_shop_schema(db: Session, shop_id: str) -> str:
    schema_name = shop_schema_name(shop_id)
    schema_quoted = f'"{schema_name}"'
    try:
        db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_quoted}"))
        db.execute(text(f"SET search_path TO {schema_quoted}"))
        Base.metadata.create_all(bind=db.connection())
        db.execute(
            text(
                "ALTER TABLE IF EXISTS products ADD COLUMN IF NOT EXISTS in_stock BOOLEAN"
            )
        )
        db.execute(
            text("ALTER TABLE IF EXISTS products ADD COLUMN IF NOT EXISTS tags TEXT")
        )
        db.commit()
    except Exception:
        db.rollback()
        settings.logger.exception("Error ensuring shop schema")
        raise
    return schema_name


def get_shop_db(shop_id: str, db: Session = Depends(db_settings.get_db)) -> Session:
    ensure_shop_schema(db, shop_id)
    return db
