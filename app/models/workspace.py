from sqlalchemy import Column,String,DateTime,Text,func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(
        UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    name = Column(String(255),nullable=False,unique=True)
    description = Column(Text,nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    