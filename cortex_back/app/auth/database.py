from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base de datos local para usuarios y logs
from app.core.config import AUTH_DB_PATH
SQLALCHEMY_DATABASE_URL = f"sqlite:///{AUTH_DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_auth_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()