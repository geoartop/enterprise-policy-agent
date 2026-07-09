from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    # These fields have no defaults, so Pydantic will error if they aren't in the .env file
    postgres_user: str
    postgres_password: str
    postgres_db: str
    google_api_key: str
    
    # These fields have fallback defaults if missing from .env
    postgres_host: str
    postgres_port: int = 5432
    embedding_model: str
    llm_model: str
    collection_name: str
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
