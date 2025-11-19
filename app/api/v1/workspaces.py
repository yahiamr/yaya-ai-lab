from typing import List
from uuid import UUID

from fastapi import HTTPException,APIRouter,Depends,status
from sqlalchemy.orm import session

from app.db.session import get_db
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate,WorkspaceRead
from app.schemas.knowledge_base import KnowledgeBaseRead
router = APIRouter()

@router.post(
    "/workspaces",
    response_model=WorkspaceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_workspace(
    payload: WorkspaceCreate,
    db: session = Depends(get_db),
) -> WorkspaceRead:
    existing = db.query(Workspace).filter(Workspace.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace with this name already exists.",
        )
    workspace = Workspace(
        name = payload.name,
        description=payload.description,
    )

    db.add(workspace)

    try:
        db.commit()
    except Exception:
        db.rollback()
    
    db.refresh(workspace)

    return workspace
    
@router.get(
    "/workspaces",
    response_model=List[WorkspaceRead]
)
def list_workspaces(
    db: session = Depends(get_db),
) -> List[WorkspaceRead]:
    workspaces = db.query(Workspace).order_by(Workspace.created_at.desc()).all()
    return workspaces


# just to test the relationships concept
@router.get(
    "/workspaces/{id}",
    response_model=List[KnowledgeBaseRead]
)
def list_kb_per_ws(id:UUID,db: session = Depends(get_db),) -> List[KnowledgeBaseRead]:
    ws = db.query(Workspace).filter(Workspace.id == id).first()
    return ws.knowledge_bases