from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id",ondelete="CASCADE"),
        nullable=False,
    )

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    # ORM relationship back to Workspace
    workspace = relationship(
        "Workspace",
        back_populates="knowledge_bases"
        )

    collections= relationship(
        "collections",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )
