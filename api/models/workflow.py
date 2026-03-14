from sqlalchemy import Column, String, ForeignKey, DateTime, UUID, Integer
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
    order = Column(Integer)
    created_at=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at= Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey(Workflow.id))
    status = Column(String, default="pending")
    trigger_payload = Column(JSONB)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at= Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ActionExecution(Base):
    __tablename__ = "action_executions"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey(WorkflowRun.id))
    action_id = Column(UUID(as_uuid=True), ForeignKey(Action.id))
    status = Column(String, default="pending")
    retry_count = Column(Integer)
    error_message = Column(String)
    output = Column(JSONB)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at= Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
