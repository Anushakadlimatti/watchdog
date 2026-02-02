from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str
    password: str

class UserCreate(UserBase):
    pass

class WorkflowBase(BaseModel):
    name: str
    status: str
    description: str


