from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:Anusha@localhost:5432/watchdog")
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)