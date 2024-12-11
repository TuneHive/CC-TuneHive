from pydantic_settings import BaseSettings


class Config(BaseSettings):
    db_username: str
    db_password: str
    db_name: str
    db_connection_name: str
    secret_key: str
    bucket_name: str
    google_application_credentials: str | None = None

    class Config:
        env_file = ".env"  # Optional, for local development


config = Config()
