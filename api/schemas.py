from pydantic import BaseModel
from typing import Optional, Any, Dict
from uuid import UUID


# ------------------ USER SCHEMAS ----------------
class UserBase(BaseModel):
    username: str
    email: str
    password: str

class UserCreate(UserBase):
    pass

class UserRead(BaseModel):
    id: UUID
    username: str
    email: str

    class Config:
        from_attributes = True   # converts SQLAlchemy → Pydantic


# ------------------ WORKFLOW SCHEMAS --------------------
class WorkflowBase(BaseModel):
    name: str
    status: str
    description: str

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None

class WorkflowCreate(WorkflowBase):
    user_id: UUID

class WorkflowRead(WorkflowBase):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True

# Trigger Schemas

class TriggerBase(BaseModel):
    type: str
    config: Dict[str, Any]

# class TriggerCreate(TriggerBase):
#     workflow_id: UUID

class TriggerUpdate(TriggerBase):
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class TriggerRead(TriggerBase):
    workflow_id: UUID
    id: UUID

    class Config:
        from_attributes: True

class ActionBase(BaseModel):
    type: str
    config: Dict[str, Any]
    order: int

class ActionUpdate(ActionBase):
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    order: Optional[int]

class ActionRead(ActionBase):
    id: UUID
    workflow_id: UUID

    class Config:
        from_attributes = True
