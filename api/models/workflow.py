from sqlalchemy import Column, String, ForeignKey, DateTime, UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class User(Base):
    __tablename__= "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id))
    name = Column(String)
    status = Column(String)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone), onupdate=lambda: datetime.now(timezone))

class Trigger(Base):
    __tablename__ = "triggers"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey(Workflow.id))
    type = Column(String)
    config = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Action(Base):
    __tablename__ = "actions"
    id = Column(UUID(as_uuid=True), primary_key=True, index= True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey(Workflow.id))
    type = Column(String)
    config = Column(JSONB, nullable=False)
    created_at=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at= Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))