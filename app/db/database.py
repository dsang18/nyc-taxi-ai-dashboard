from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config

engine = create_engine(str(Config.SQLALCHEMY_DATABASE_URI))

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)