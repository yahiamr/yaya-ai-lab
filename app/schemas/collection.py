from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class CollectionBase(BaseModel):
    name:str
    description:str|None=None

class CollectionCreate(CollectionBase):
    """
    Schema for creating a new collection within a knowledge base.
    """
    pass
class CollectionRead(CollectionBase):
    """
    Schema for reading / returning collection data.
    """

    id: UUID
    knowledge_base_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)