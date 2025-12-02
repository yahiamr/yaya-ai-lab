from typing import List
from uuid import UUID
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.collection import Collection
from app.models.document import Document
from app.schemas.document import DocumentRead
from app.services.storage import get_default_storage_backend


router = APIRouter()


def _get_collection_or_404(collection_id: UUID, db: Session) -> Collection:
    """
    Helper to fetch a collection or raise 404.
    """
    collection = (
        db.query(Collection)
        .filter(Collection.id == collection_id)
        .first()
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )
    return collection


@router.post(
    "/collections/{collection_id}/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    collection_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentRead:
    """
    Upload a single document into a collection.

    Stores the file using the default storage backend and creates
    a Document record in the database.
    """
    _get_collection_or_404(collection_id, db)

    storage = get_default_storage_backend()

    file_bytes = await file.read()
    size_bytes = len(file_bytes)

    safe_filename = file.filename or "unnamed"
    doc_id = uuid.uuid4()
    relative_path = f"collections/{collection_id}/documents/{doc_id}/{safe_filename}"

    storage_path = storage.save(relative_path, file_bytes)

    document = Document(
        id=doc_id,
        collection_id=collection_id,
        filename=safe_filename,
        mime_type=file.content_type,
        size_bytes=size_bytes,
        storage_path=storage_path,
        status="ready",
    )

    db.add(document)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(document)

    return document


@router.get(
    "/collections/{collection_id}/documents",
    response_model=List[DocumentRead],
)
def list_documents(
    collection_id: UUID,
    db: Session = Depends(get_db),
) -> List[DocumentRead]:
    """
    List documents for a given collection.
    """
    _get_collection_or_404(collection_id, db)

    docs = (
        db.query(Document)
        .filter(Document.collection_id == collection_id)
        .order_by(Document.created_at.desc())
        .all()
    )

    return docs