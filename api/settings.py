from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Configurable settings, got from environment"""
    # SECURITY
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    SECRET_KEY: str = "235to789yw3rgy789owerfh0p89q2f34"

    # SMTP
    SMTP_LOGIN: str
    SMTP_PASSWORD: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_FROM_EMAIL: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


SETTINGS = AppSettings()
