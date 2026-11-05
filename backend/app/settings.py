from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str
    secret_key: str
    frontend_origin: str = "https://www.banxia.xin"
    session_ttl_hours: int = 168
    cookie_secure: bool = True

settings = Settings()
