from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DatasetBase(BaseModel):
    name: str


class DatasetCreate(DatasetBase):
    """
    Schema for creating a new dataset.

    The CSV file itself is uploaded separately via multipart/form-data;
    this schema represents the JSON fields (e.g. name).
    """
    pass


class DatasetRead(DatasetBase):
    """
    Schema for reading / returning dataset metadata.
    """

    id: UUID
    workspace_id: UUID
    filename: str
    mime_type: str | None
    size_bytes: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
