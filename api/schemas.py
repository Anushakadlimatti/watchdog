from pydantic import BaseModel
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

class WorkflowCreate(WorkflowBase):
    user_id: UUID

class WorkflowRead(WorkflowBase):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True