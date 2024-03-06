from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    description_tfidf_matrices: dict = {}
    price_vector: list = []
    description_tfidf_file_name: str = "description_tfidf.pkl"
    price_vector_file_name: str = "price_vector.pkl"


settings = Settings()
