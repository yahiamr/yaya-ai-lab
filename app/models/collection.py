from sqlalchemy import Column,Text, String,DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base

class Collection(Base):
    __tablename__ = "collections"

    id= Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    knowledge_base_id= Column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_bases.id",ondelete="CASCADE"),
        nullable=False,
    )

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    knowledge_base = relationship("KnowlegeBase",back_populates="collections")