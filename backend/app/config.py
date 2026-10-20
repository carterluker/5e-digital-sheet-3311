from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    database_url: str = "postgresql+psycopg://sheet:sheet@localhost:5432/sheet"
    cors_origins: list[str] = ["http://localhost:5173"]

    session_ttl_hours: int = 24 * 7
    # Set to true when served over HTTPS so the session cookie is never sent in the clear.
    cookie_secure: bool = False
    # A backup of the previous state is taken on save if the newest backup is older than this.
    backup_interval_seconds: int = 300
    max_backups_per_character: int = 20


settings = Settings()
