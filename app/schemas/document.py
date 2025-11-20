from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class DocumentRead(BaseModel):
    """
    Schema for reading / returning document metadata.
    """

    id: UUID
    collection_id: UUID
    filename: str
    mime_type: str | None
    size_bytes: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
