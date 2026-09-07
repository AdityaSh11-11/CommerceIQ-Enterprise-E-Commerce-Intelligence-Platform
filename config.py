from sqlalchemy import create_engine
import os

DATABASE_URL = "sqlite:///commerceiq.db"

engine = create_engine(DATABASE_URL)
