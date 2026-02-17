import re

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.config import db_settings, settings
from app.models.base import Base

SHOP_ID_PATTERN = re.compile(r"^[a-z0-9_]+$")


def _normalize_shop_id(shop_id: str) -> str:
    if shop_id is None:
        raise ValueError("shop_id is required")
    normalized = shop_id.strip().lower()
    if not normalized or not SHOP_ID_PATTERN.match(normalized):
        raise ValueError("shop_id must be lowercase alphanumeric with underscores only")
    return normalized


def _shop_schema_name(shop_id: str) -> str:
    normalized = _normalize_shop_id(shop_id)
    return f"shop_{normalized}"


def _ensure_shop_schema(schema_name: str) -> None:
    engine = db_settings._get_engine()
    schema_quoted = f'"{schema_name}"'
    try:
        with engine.begin() as connection:
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_quoted}"))
            connection.execute(text(f"SET search_path TO {schema_quoted}"))
            Base.metadata.create_all(bind=connection)
    except Exception:
        settings.logger.exception("Error ensuring shop schema")
        raise


def get_shop_session(shop_id: str):
    schema_name = _shop_schema_name(shop_id)
    _ensure_shop_schema(schema_name)
    engine = db_settings._get_engine()
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_local()
    session.execute(text(f'SET search_path TO "{schema_name}"'))
    return session
