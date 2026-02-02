from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__= "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    created_at = Column(DateTime)

class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id))
    name = Column(String)
    status = Column(String)
    description = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)