from fastapi import FastAPI, Depends
from config.database import sessionLocal, engine
from sqlalchemy.orm import Session
from models.workflow import User, Base
from schemas import UserCreate
from uuid import uuid4
from datetime import datetime

app = FastAPI()

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def health_test():
    return "Healthy and Running"

@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        id=uuid4(),
        username=user.username,
        email=user.email,
        password=user.password,
        created_at=datetime.now()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user