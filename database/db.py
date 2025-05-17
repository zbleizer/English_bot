from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base


SQLITE_DB = "sqlite:///english.db"
engine = create_engine(SQLITE_DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)