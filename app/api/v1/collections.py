from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.knowledge_base import KnowledgeBase
from app.models.collection import Collection
from app.schemas.knowledge_base import KnowledgeBaseRead
from app.schemas.collection import CollectionCreate, CollectionRead

router = APIRouter()


def _get_kb_or_404(knowledge_base_id: UUID, db: Session) -> KnowledgeBase:
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found.",
        )
    return kb


@router.post(
    "/knowledge-bases/{knowledge_base_id}/collections",
    response_model=CollectionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_collection(
    knowledge_base_id: UUID,
    payload: CollectionCreate,
    db: Session = Depends(get_db),
) -> CollectionRead:
    # check kb esists
    _get_kb_or_404(knowledge_base_id=knowledge_base_id, db=db)
    # one collection name per kb
    existing = (
        db.query(Collection)
        .filter(
            Collection.knowledge_base_id == knowledge_base_id,
            Collection.name == payload.name,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collection with this name already exists in this knowledge base.",
        )

    collection = Collection(
        knowledge_base_id=knowledge_base_id,
        name=payload.name,
        description=payload.description,
    )

    db.add(collection)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(collection)

    return collection

@router.get(
    "/knowledge-bases/{knowledge_base_id}/collections",
    response_model=List[CollectionRead],
)
def list_collections(
    knowledge_base_id:UUID,
    db:Session=Depends(get_db),
) -> List[CollectionRead]:
    _get_kb_or_404(knowledge_base_id=knowledge_base_id,db=db)
    collections = db.query(Collection).filter(Collection.knowledge_base_id== knowledge_base_id).order_by(Collection.created_at.desc()).all()

    return collections