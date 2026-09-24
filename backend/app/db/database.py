from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# In PostgreSQL, we can use the URL directly.
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
