from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: SecretStr

    # MongoDB
    MONGO_URI: str
    MONGO_DB_NAME: str | None = None  # если не указан, будет извлечён из URI

    model_config = SettingsConfigDict(
        env_file_encoding='utf-8',
        env_nested_delimiter='',
    )

config = Settings()
