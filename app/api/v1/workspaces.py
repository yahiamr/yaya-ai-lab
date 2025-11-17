from typing import List

from fastapi import HTTPException,APIRouter,Depends,status
from sqlalchemy.orm import session

from app.db.session import get_db
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate,WorkspaceRead

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