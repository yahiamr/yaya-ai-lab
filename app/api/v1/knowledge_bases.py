from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.workspace import Workspace
from app.models.knowledge_base import KnowledgeBase
from app.schemas.knowledge_base import KnowledgeBaseCreate,KnowledgeBaseRead

router = APIRouter()

def _get_workspace_or_404(workspace_id: UUID, db: Session) -> Workspace:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )
    return workspace

@router.post(
    "/workspaces/{workspace_id}/knowledge-bases",
    response_model=KnowledgeBaseRead,
    status_code=status.HTTP_201_CREATED
)
def create_knowledge_base(
    workspace_id: UUID,
    payload: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
) -> KnowledgeBaseRead:
    # make sure workspace exists   
    _get_workspace_or_404(workspace_id,db)

    # enforce unique name per workspace 
    existing = (
        db.query(KnowledgeBase)
        .filter(
        KnowledgeBase.workspace_id == workspace_id,
        KnowledgeBase.name == payload.name,
            )
        .first())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Knowledge base with this name already exists in this workspace.",
        )
    kb = KnowledgeBase(
        workspace_id = workspace_id,
        name = payload.name,
        description = payload.description,
    )

    db.add(kb)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(kb)
    return kb

@router.get("workspaces/{workspace_id}/knowledge-bases",response_model=List[KnowledgeBaseRead],)
def list_knowledge_bases(workspace_id: UUID,db: Session = Depends(get_db),) -> List[KnowledgeBaseRead]:
    _get_workspace_or_404(
        workspace_id=workspace_id,
        db=db,
    )
    
    kbs = (
    db.query(KnowledgeBase)
    .filter(KnowledgeBase.workspace_id == workspace_id)
    .order_by(KnowledgeBase.created_at.desc())
    .all()
    )
    return kbs
