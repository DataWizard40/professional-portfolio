from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings, read from environment variables or a .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "mysql+pymysql://app:app@localhost:3306/library"
    loan_days: int = 14  # how long a member can keep a book
    max_active_loans: int = 3  # how many books a member can borrow at once


settings = Settings()
