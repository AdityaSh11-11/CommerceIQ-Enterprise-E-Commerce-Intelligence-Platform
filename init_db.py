from sqlalchemy import inspect

from database import engine
from models import Base

Base.metadata.create_all(engine)

print("=" * 50)
print("Database Initialized")
print("=" * 50)

inspector = inspect(engine)

print("Tables Created")

for table in inspector.get_table_names():
    print("✓", table)