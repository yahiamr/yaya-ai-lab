from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class KnowledgeBaseBase(BaseModel):
    name: str
    description: str | None = None

class KnowledgeBaseCreate(KnowledgeBaseBase):
    """
    Schema for creating a new knowledge base within a workspace.
    """
    pass

class KnowledgeBaseRead(KnowledgeBaseBase):
    """
    Schema for reading / returning knowledge base data.
    """

    id: UUID
    workspace_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)