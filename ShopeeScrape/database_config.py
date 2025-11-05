from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base



SQLalchamy_DB_URL = ''

engine = create_engine(SQLalchamy_DB_URL)

SessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)

Base = declarative_base

def get_db():
    db = SessionLocal()
    
    try:
        yield db
    finally:
        db.close()