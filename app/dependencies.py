from sqlmodel import create_engine, Session
from config import Config

# Read env variables
config = Config()

connection_string = f"mysql://{config.db_username}:{config.db_password}@{config.db_host}:{config.db_post}/{config.db_name}"
connect_args = {"check_same_thread": False}

engine = create_engine(connection_string, connect_args=connect_args)

def get_session():
  with Session(engine) as session:
    yield session