from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models import TextData
from service.user_text_crud import (
    create_user_text,
    update_user_text,
    delete_user_text,
    get_user_text,
    get_user_text_list,
)
from user_auth.routes import get_db
from user_auth.utils.auth_wrapper import require_roles

router = APIRouter(prefix="/user_text", tags=["user_text"])


@router.post("/create")
async def api_create_user_text(
    user_text_data: TextData,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin", "user"])),
):
    return await create_user_text(user_text_data, db=db, user_id=user.id)


@router.get("/get/{user_text_id}")
async def api_get_user_text(
    user_text_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin", "user"])),
):
    return await get_user_text(user_text_id, db=db, user_id=user.id)


@router.get("/all")
async def api_get_user_text_list(
    limit: int | None = None,
    offset: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin", "user"])),
):
    return await get_user_text_list(limit, offset, db=db, user_id=user.id)


@router.post("/update")
async def api_update_user_text(
    user_text_data: TextData,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin", "user"])),
):
    return await update_user_text(user_text_data, db=db, user_id=user.id)


@router.get("/delete/{user_text_id}")
async def api_delete_user_text(
    user_text_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin", "user"])),
):
    return await delete_user_text(user_text_id, db=db, user_id=user.id)
