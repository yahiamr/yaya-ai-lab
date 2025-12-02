from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Human-readable name for the dataset (could differ from filename)
    name = Column(String(255), nullable=False)

    # Original uploaded filename
    filename = Column(String(512), nullable=False)

    mime_type = Column(String(255), nullable=True)
    size_bytes = Column(Integer, nullable=False)
    storage_path = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    workspace = relationship("Workspace", back_populates="datasets")
