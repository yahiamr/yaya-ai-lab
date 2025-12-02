from fastapi import APIRouter

from app.api.v1 import workspaces
from app.api.v1 import knowledge_bases
from app.api.v1 import collections
from app.api.v1 import documents
from app.api.v1 import datasets

api_router = APIRouter()

api_router.include_router(
    workspaces.router,
    prefix="",
    tags=["workspaces"],
)

api_router.include_router(
    knowledge_bases.router,
    prefix="",
    tags=["knowledge-bases"],
)

api_router.include_router(
    collections.router,
    prefix="",
    tags=["collections"]
)

api_router.include_router(
    documents.router,
    prefix="",
    tags=["documents"],
)

api_router.include_router(
    datasets.router,
    prefix="",
    tags=["datasets"],
)
