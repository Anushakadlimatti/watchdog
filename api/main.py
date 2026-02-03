from fastapi import FastAPI, Depends
from config.database import sessionLocal, engine
from sqlalchemy.orm import Session
from models.workflow import User, Base, Workflow
from schemas import UserCreate, WorkflowCreate, WorkflowRead
from uuid import UUID, uuid4
from datetime import datetime, timezone

app = FastAPI()

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)     # create table in db

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
        created_at=datetime.now(timezone.utc)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get all workflows
@app.get("/workflows", response_model=list[WorkflowRead])
def get_all_workflows(db: Session = Depends(get_db)):
    all_workflows = db.query(Workflow).all()
    return all_workflows

# Get workflow by id
@app.get("/workflows/{id}", response_model=WorkflowRead)
def get_workflow_by_id(id: UUID, db: Session = Depends(get_db)):
    workflow = db.query(Workflow).filter(Workflow.id == id).first()
    if workflow is None:
        return {"detail": "Workflow not found"}
    return workflow

# Create workflow
@app.post("/workflows", response_model=WorkflowRead)
def add_workflow(data: WorkflowCreate, db: Session = Depends(get_db)):
    new_workflow = Workflow(
        id=uuid4(),
        user_id=data.user_id,
        name=data.name,
        status=data.status,
        description=data.description,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(new_workflow)
    db.commit()
    db.refresh(new_workflow)
    return new_workflow