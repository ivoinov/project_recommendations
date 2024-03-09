from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv


class Settings(BaseSettings):
    description_tfidf_matrices: dict = {}
    price_vectors: dict = {}
    description_tfidf_file_name: str = "description_tfidf.pkl"
    price_vector_file_name: str = "price_vector.pkl"


global settings, ACCESS_TOKEN_EXPIRE_MINUTES
settings = Settings()

load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
