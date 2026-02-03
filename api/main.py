from fastapi import FastAPI, Depends, HTTPException, status
from config.database import sessionLocal, engine
from sqlalchemy.orm import Session
from models.workflow import User, Base, Workflow
from schemas import UserCreate, WorkflowCreate, WorkflowRead, WorkflowUpdate, UserRead
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

@app.post("/users", response_model=UserRead, status_code=status.HTTP_200_OK)
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

# Response model is to structure the response(not to send all the fields in db)
@app.get("/users", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)):
    all_users = db.query(User).all()
    return all_users

# Get all workflows
@app.get("/users/{userId}/workflows", response_model=list[WorkflowRead])
def get_all_workflows(userId: UUID, db: Session = Depends(get_db)):
    all_workflows = db.query(Workflow).filter(Workflow.user_id == userId).all()
    return all_workflows


# Get workflow by id
@app.get("/workflows/{id}", response_model=WorkflowRead, status_code=status.HTTP_200_OK)
def get_workflow_by_id(id: UUID, db: Session = Depends(get_db)):
    workflow = db.query(Workflow).filter(Workflow.id == id).first()
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return workflow

# Create workflow
@app.post("/workflows", response_model=WorkflowRead, status_code=status.HTTP_201_CREATED)
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
    try:
        db.add(new_workflow)
        db.commit()
        db.refresh(new_workflow)
        return new_workflow
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow creation failed"
        )

# Update workflow
@app.put("/workflows/{workflowId}", response_model=WorkflowRead, status_code=status.HTTP_200_OK)
def update_workflow(workflowId: UUID, workflow: WorkflowUpdate, db:Session = Depends(get_db)):
    workflow_to_update = db.query(Workflow).filter(Workflow.id == workflowId).first()
    if not workflow_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )

    if workflow.name is not None:
        workflow_to_update.name = workflow.name
    if workflow.description is not None:
        workflow_to_update.description = workflow.description
    if workflow.status is not None:
        workflow_to_update.status = workflow.status

    workflow_to_update.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(workflow_to_update)
    return workflow_to_update
    
# Delete workflow
@app.delete("/workflows/{workflowId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(workflowId: UUID, db: Session = Depends(get_db)):
    workflow_to_delete = db.query(Workflow).filter(Workflow.id == workflowId).first()
    if not workflow_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    db.delete(workflow_to_delete)
    db.commit()
    return "Workflow deleted successfully."
