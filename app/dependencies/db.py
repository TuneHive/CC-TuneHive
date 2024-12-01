from sqlmodel import create_engine, Session
from ..config import Config
from fastapi import Depends
from typing import Annotated

# Read env variables
config = Config()

connection_string = f"mysql+pymysql://{config.db_username}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}"
connect_args = {"check_same_thread": False}

engine = create_engine(connection_string)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
