from typing import List
from uuid import UUID
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.workspace import Workspace
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetRead
from app.services.storage import get_default_storage_backend


router = APIRouter()


def _get_workspace_or_404(workspace_id: UUID, db: Session) -> Workspace:
    """
    Helper to fetch a workspace or raise 404.
    """
    workspace = (
        db.query(Workspace)
        .filter(Workspace.id == workspace_id)
        .first()
    )
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )
    return workspace


@router.post(
    "/workspaces/{workspace_id}/datasets",
    response_model=DatasetRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_dataset(
    workspace_id: UUID,
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DatasetRead:
    """
    Upload a CSV dataset into a workspace.

    The dataset gets a logical name, and the CSV file is stored using
    the default storage backend.
    """
    _get_workspace_or_404(workspace_id, db)

    content_type = file.content_type or ""
    if "csv" not in content_type.lower() and not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file does not look like a CSV (content-type or extension mismatch).",
        )

    storage = get_default_storage_backend()

    file_bytes = await file.read()
    size_bytes = len(file_bytes)

    safe_filename = file.filename or "dataset.csv"

    dataset_id = uuid.uuid4()

    relative_path = f"workspaces/{workspace_id}/datasets/{dataset_id}/{safe_filename}"

    storage_path = storage.save(relative_path, file_bytes)

    dataset = Dataset(
        id=dataset_id,
        workspace_id=workspace_id,
        name=name,
        filename=safe_filename,
        mime_type=file.content_type,
        size_bytes=size_bytes,
        storage_path=storage_path,
    )

    db.add(dataset)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(dataset)

    return dataset


@router.get(
    "/workspaces/{workspace_id}/datasets",
    response_model=List[DatasetRead],
)
def list_datasets(
    workspace_id: UUID,
    db: Session = Depends(get_db),
) -> List[DatasetRead]:
    """
    List datasets for a given workspace.
    """
    _get_workspace_or_404(workspace_id, db)

    datasets = (
        db.query(Dataset)
        .filter(Dataset.workspace_id == workspace_id)
        .order_by(Dataset.created_at.desc())
        .all()
    )

    return datasets
