from sqlalchemy import column,String,DateTime,text,func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base

class Workspace(Base):
    __tablename__ = "workspaces"

    id = column(
        UUID(as_uuid=True),
        primary_key = True,
        default = uuid.uuid4,
    )

    name = column(String(255),nullable=False,unique=True)
    description = column(text,nullable=True)
    created_at = column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    