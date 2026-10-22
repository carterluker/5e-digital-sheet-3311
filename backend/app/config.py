from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    database_url: str = "postgresql+psycopg://sheet:sheet@localhost:5432/sheet"
    database_connect_timeout: int = 10 # Seconds
    cors_origins: list[str] = ["http://localhost:5173"]
    session_lifetime_hours: int = 24 * 7

    # default_user = None, if you don't want a default user.
    default_user: dict = {
        "username": "BennyTheBengal",
        "password": "VandalsSuck"
    }


settings = Settings()