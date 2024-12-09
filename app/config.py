from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    db_username: str
    db_password: str
    db_name: str
    db_connection_name: str
    secret_key: str
    bucket_name: str
    google_application_credentials: str | None

    model_config = SettingsConfigDict(env_file=".env")


config = Config()
