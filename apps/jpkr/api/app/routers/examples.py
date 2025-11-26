from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from models import ExampleCreate, ExampleUpdate, ExampleFilterData
from service.admin.examples_crud import (
    create_examples_batch,
    update_examples_batch,
    delete_examples_batch,
)
from service.admin.filter_examples import filter_examples_by_criteria
from service.feed_examples import get_examples_for_user
from user_auth.routes import get_db
from user_auth.utils.auth_wrapper import require_roles
router = APIRouter(prefix="/examples", tags=["examples"])


class ExamplesForUserRequest(BaseModel):
    tags: Optional[List[str]] = None


@router.post("/create/batch")
async def api_create_examples(
    examples_data: List[ExampleCreate],
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"])),
):
    return create_examples_batch(examples_data, db=db, user_id=user.id)


@router.post("/update/batch")
async def api_update_examples(
    examples_data: List[ExampleUpdate],
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"])),
):
    return update_examples_batch(examples_data, db=db, user_id=user.id)


@router.post("/delete/batch")
async def api_delete_examples(
    example_ids: List[int],
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"])),
):
    return delete_examples_batch(example_ids, db=db, user_id=user.id)


@router.post("/filter")
async def api_filter_examples(
    example_filter_data: ExampleFilterData,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"])),
):
    return filter_examples_by_criteria(
        db=db, user_id=user.id, **example_filter_data.model_dump()
    )


@router.post("/get-examples-for-user")
async def api_get_examples_for_user(
    payload: ExamplesForUserRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["*"])),
):
    print(payload.tags)
    return get_examples_for_user(
        tags=payload.tags, db=db, user_id=user.id if user else None
    )
