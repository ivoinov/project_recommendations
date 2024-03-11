from pydantic_settings import BaseSettings
import os, logging
from logging.handlers import RotatingFileHandler
from logging import Logger
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

load_dotenv()


def get_defined_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    filepath = os.path.join(os.getcwd(), "var", "app.log")
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    file_handler = RotatingFileHandler(filepath, maxBytes=10000000, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


class Settings(BaseSettings):
    project_root: str = os.getcwd()
    logger: Logger = get_defined_logger()
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    SECRET_KEY: str = str(os.getenv("SECRET_KEY"))
    ALGORITHM: str = "HS256"
    description_tfidf_matrices: dict = {}
    price_vectors: dict = {}
    description_tfidf_file_name: str = "description_tfidf.pkl"
    price_vector_file_name: str = "price_vector.pkl"


class Database(BaseSettings):
    DATABASE_URL: str = str(os.getenv("DATABASE_URL"))

    def get_db(self):
        SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=create_engine(self.DATABASE_URL)
        )
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


global settings, db_settings
settings = Settings()
db_settings = Database()
