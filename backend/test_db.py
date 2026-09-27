from sqlalchemy import create_engine, inspect
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)
for col in inspector.get_columns('analyses'):
    if col['name'] == 'created_at':
        print("Column details:", col)
