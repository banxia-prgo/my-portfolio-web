from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)
    database_url: str | None = None
    postgres_user: str = "banxia"
    postgres_password: str = ""
    postgres_db: str = "banxia"
    postgres_host: str = "db"
    secret_key: str
    frontend_origin: str = "https://www.banxia.xin"
    session_ttl_hours: int = 168
    cookie_secure: bool = True
    # Comma-separated bootstrap administrator emails; never expose this value to clients.
    admin_emails: str = ""
    media_public_origin: str = "https://api.banxia.xin"

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        password = quote_plus(self.postgres_password)
        return f"postgresql+psycopg://{self.postgres_user}:{password}@{self.postgres_host}:5432/{self.postgres_db}"

settings = Settings()
