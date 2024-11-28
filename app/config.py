from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
  db_username: str
  db_password: str
  db_host: str
  db_post: str
  db_name: str

  model_config = SettingsConfigDict(env_file="./../.env")