"""
Centralized application settings, loaded from environment variables / .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/elearning_db"

    # Cloudinary
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # AI content generation
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Auth
    secret_key: str = "insecure-dev-secret-change-me"
    access_token_expire_minutes: int = 1440

    # CORS
    frontend_origin: str = "http://localhost:3000"


settings = Settings()
