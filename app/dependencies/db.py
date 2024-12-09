from sqlmodel import create_engine, Session
from ..config import config
from fastapi import Depends
from typing import Annotated
from google.cloud.sql.connector import Connector, IPTypes
import pymysql


def connect_with_connector():
    """
    Initializes a connection pool for a Cloud SQL instance of MySQL.
    """
    instance_connection_name = config.db_connection_name
    db_user = config.db_username
    db_pass = config.db_password
    db_name = config.db_name
    ip_type = IPTypes.PUBLIC

    connector = Connector(ip_type)

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

    engine = create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    return engine


engine = connect_with_connector()


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
