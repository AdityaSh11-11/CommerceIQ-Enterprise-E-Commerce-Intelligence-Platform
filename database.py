from sqlalchemy import create_engine

from config import DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={
        "check_same_thread": False
    }
)