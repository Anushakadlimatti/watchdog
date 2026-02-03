from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)