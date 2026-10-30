from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/tasktracker"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()