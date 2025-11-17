from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, BaseModel

class WorkspaceBase(BaseModel):
    name: str
    description: str | None = None

class WorkspaceCreate(WorkspaceBase):
    """
    Schema for creating a new workspace.

    At creation time we only need:
    - name (required)
    - description (optional)
    """
    pass

class WorkspaceRead(WorkspaceBase):
    """
    Schema for reading / returning workspace data.

    Includes:
    - id: UUID
    - created_at: timestamp
    plus the fields from WorkspaceBase.
    """
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes = True)
