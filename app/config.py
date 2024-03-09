from pydantic_settings import BaseSettings
import os, logging
from logging import Logger
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    project_root: str = os.getcwd()
    logger: Logger = logging.getLogger(__name__)
    DATABASE_URL: str = str(os.getenv("DATABASE_URL"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    SECRET_KEY: str = str(os.getenv("SECRET_KEY"))
    ALGORITHM: str = "HS256"
    description_tfidf_matrices: dict = {}
    price_vectors: dict = {}
    description_tfidf_file_name: str = "description_tfidf.pkl"
    price_vector_file_name: str = "price_vector.pkl"


global settings
settings = Settings()
