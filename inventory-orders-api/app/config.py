from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings, read from environment variables or a .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "mysql+pymysql://app:app@localhost:3306/inventory"
    secret_key: str = "dev-secret-key-change-me-in-production-0123456789"
    access_token_expire_minutes: int = 60


settings = Settings()
