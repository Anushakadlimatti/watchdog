from fastapi import FastAPI, Depends, HTTPException, status, Request
from config.database import sessionLocal, engine
from sqlalchemy.orm import Session
from models.workflow import User, Base, Workflow, Trigger, Action, WorkflowRun, ActionExecution
from schemas import UserCreate, WorkflowCreate, WorkflowRead, WorkflowUpdate, UserRead, TriggerRead, TriggerBase, TriggerUpdate, ActionBase, ActionRead, ActionUpdate
from uuid import UUID, uuid4
from datetime import datetime, timezone
import requests

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

@app.get("/workflows/{workflowId}/triggers", response_model=list[TriggerRead], status_code=status.HTTP_200_OK)
def getAllTriggers(workflowId: UUID, db: Session = Depends(get_db)):
    workflowExists = db.query(Workflow).filter(Workflow.id == workflowId).first()

    if not workflowExists:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found."
        )
    
    triggers = db.query(Trigger).filter(Trigger.workflow_id == workflowId).all()
    return triggers

@app.post("/workflows/{workflowId}/triggers", response_model=TriggerRead, status_code=status.HTTP_201_CREATED)
def addTrigger(workflowId: UUID, data: TriggerBase, db: Session = Depends(get_db)):
    workflowExists = db.query(Workflow).filter(Workflow.id == workflowId).first()
    if not workflowExists:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found."
        )
    new_trigger = Trigger(
        id= uuid4(),
        workflow_id= workflowId,
        type = data.type,
        config = data.config,
        created_at = datetime.now(timezone.utc),
        updated_at = datetime.now(timezone.utc)
    )
    try:
        db.add(new_trigger)
        db.commit()
        db.refresh(new_trigger)
        return new_trigger
    except Exception as e:
        db.rollback()
        print(e, "error")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad Request"
        )

@app.put("/workflows/{workflowId}/triggers/{triggerId}", response_model=TriggerRead, status_code=status.HTTP_200_OK)
def updateTrigger(workflowId: UUID, triggerId: UUID, data: TriggerUpdate, db: Session = Depends(get_db)):
    workflowExits = db.query(Workflow).filter(Workflow.id == workflowId).first()
    trigger_to_update = db.query(Trigger).filter(Trigger.id == triggerId).first()

    if not workflowExits:
        raise HTTPException(
            status_code=404,
            detail="Workflow not exits."
        )
    
    if not trigger_to_update:
        raise HTTPException(
            status_code=404,
            detail="Trigger not found."
        )
    
    if data.type is not None:
        trigger_to_update.type = data.type
    if data.config is not None:
        trigger_to_update.config = data.config
    trigger_to_update.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(trigger_to_update)
        return trigger_to_update
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=400,
            detail="Failed to update trigger"
        )
    
@app.delete("/workflows/{workflow}/triggers/{triggerId}", status_code=status.HTTP_200_OK)
def removeTrigger(workflowId: UUID,triggerId: UUID, db: Session = Depends(get_db)):
    workflowExits = db.query(Workflow).filter(Workflow.id == workflowId).first()
    trigger_to_delete = db.query(Trigger).filter(Trigger.id == triggerId).first()

    if not workflowExits:
        raise HTTPException(
            status_code=404,
            detail="Workflow not exits."
        )
    
    if not trigger_to_delete:
        raise HTTPException(
            status_code=404,
            detail="Trigger not found."
        )
    
    try:
        db.delete(trigger_to_delete)
        db.commit()
        return "Trigger removed"
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=400,
            detail="Remove failed"
        )
    
@app.get("/workflows/{workflowId}/actions", response_model=list[ActionRead], status_code=status.HTTP_200_OK)
def getAllActions(workflowId: UUID, db: Session = Depends(get_db)):
    workflow_exits = db.query(Workflow).filter(Workflow.id == workflowId).first()

    if not workflow_exits:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found"
        )
    
    allActions = db.query(Action).filter(Action.workflow_id == workflowId).all()
    return allActions

@app.post("/workflows/{workflowId}/actions", response_model=ActionRead, status_code=status.HTTP_201_CREATED)
def createAction(workflowId: UUID, data: ActionBase, db: Session = Depends(get_db)):
    workflow_exits = db.query(Workflow).filter(Workflow.id == workflowId).first()

    if not workflow_exits:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found"
        )
    
    new_action = Action(
        id = uuid4(),
        workflow_id = workflowId,
        type = data.type,
        config = data.config,
        order = data.order,
        created_at = datetime.now(timezone.utc),
        updated_at = datetime.now(timezone.utc)
    )

    try:
        db.add(new_action)
        db.commit()
        db.refresh(new_action)
        return new_action
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=400,
            detail="Action creation failed."
        )
    
@app.put("/workflows/{workflowId}/actions/{actionId}", response_model=ActionRead, status_code=status.HTTP_200_OK)
def updateAction(workflowId: UUID, actionId: UUID, data: ActionUpdate, db: Session = Depends(get_db)):
    workflow_exits = db.query(Workflow).filter(Workflow.id == workflowId).first()

    if not workflow_exits:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found"
        )
    
    action_to_update = db.query(Action).filter(Action.id == actionId).first()

    if not action_to_update:
        raise HTTPException(
            status_code=404,
            detail="Action not found."
        )
    
    if data.type is not None:
        action_to_update.type = data.type
    if data.config is not None:
        action_to_update.config = data.config
    if data.order is not None:
        action_to_update.order = data.order
    action_to_update.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(action_to_update)
        return action_to_update
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=400,
            detail="Failed to updated action"
        )
    
@app.delete("/workflows/{workflowId}/actions/{actionId}", status_code=status.HTTP_200_OK)
def deleteAction(workflowId: UUID, actionId: UUID, db: Session = Depends(get_db)):
    workflow_exits = db.query(Workflow).filter(Workflow.id == workflowId).first()

    if not workflow_exits:
        raise HTTPException (
            status_code=404,
            detail="Workflow not found"
        )
    
    action_to_delete = db.query(Action).filter(Action.id == actionId, Action.workflow_id == workflowId).first()

    if not action_to_delete:
        raise HTTPException (
            status_code=404,
            detail="Action not found."
        )
    
    try:
        db.delete(action_to_delete)
        db.commit()
        return "Action deleted"
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException (
            status_code=400,
            detail="Failed to delete action"
        )

@app.post("/workflows/{workflowId}/run", status_code=status.HTTP_201_CREATED)
def ExecuteWorkflow(workflowId: UUID, db: Session = Depends(get_db)):
    workflowExists = db.query(Workflow).filter(Workflow.id == workflowId).first()

    if not workflowExists:
        raise HTTPException(
            status_code=404,
            detail="Workflow does not exists."
        )
    
    newWorkflowRun = WorkflowRun(
        workflow_id = workflowId,
        status = "pending"
    )

    db.add(newWorkflowRun)
    db.commit()
    db.refresh(newWorkflowRun)

    actions = db.query(Action).filter(Action.workflow_id == workflowId).order_by(Action.order).all()

    for action in actions:
        newActionExecution = ActionExecution(
            workflow_run_id = newWorkflowRun.id,
            action_id = action.id,
            status = "pending"
        )

        db.add(newActionExecution)
    db.commit()

    try:
        requests.post(
            "http://localhost:3000/execute",
            json={"workflow_run_id": str(newWorkflowRun.id)}
        )
    except:
        pass

    return {
        "workflow_run_id": newWorkflowRun.id,
        "status": "pending"
    }

@app.post("/webhook/{trigger_id}", status_code=status.HTTP_200_OK)
async def executeWebhookTrigger(trigger_id: UUID, request: Request, db: Session = Depends(get_db)):
    trigger = db.query(Trigger).filter(Trigger.id == trigger_id).first()

    if not trigger:
        raise HTTPException(
            status_code=404,
            detail="Trigger not exists."
        )
    
    if trigger.type != 'webhook':
        raise HTTPException(
            status_code=400,
            detail="Trigger is not webhook type."
        )
    
    secret_header = request.headers.get("x-wehbook-secret")
    if not secret_header:
        raise HTTPException(
            status_code=403,
            detail="Invalid webhook secret"
        )
    payload = await request.json()

    workflow_run = WorkflowRun(
        workflow_id = trigger.workflow_id,
        status = "pending",
        trigger_payload = payload
    )

    db.add(workflow_run)
    db.commit()
    db.refresh(workflow_run)

    actions = db.query(Action).filter(Action.workflow_id == trigger.workflow_id).order_by(Action.order).all()

    for action in actions:
        actionExecution = ActionExecution(
            workflow_run_id = workflow_run.id,
            status = "pending",
            action_id = action.id
        )

        db.add(actionExecution)
    db.commit()
    try:
        requests.post(
            "http://localhost:3000/execute",
            json={"workflow_run_id": str(workflow_run.id)}
        )
    except:
        pass
    
    return {
        "workflow_run_id": workflow_run.id,
        "status": "pending"
    }




    