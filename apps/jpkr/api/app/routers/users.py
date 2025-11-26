from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from service.user_sevice import UserService
from user_auth.routes import get_db
from user_auth.utils.auth_wrapper import require_roles

router = APIRouter(tags=["users"])


@router.get("/user_admin/get_all_users/{limit}/{offset}")
async def api_get_user_list(
    limit: int | None = None,
    offset: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"])),
):
    return UserService.get_users(limit, offset, db=db, user_id=user.id)


@router.get("/user_admin/delete/{id}")
async def api_delete_user(id: str, db: Session = Depends(get_db), user=Depends(require_roles(["admin"]))):
    return UserService.delete_user(id, db=db, user_id=user.id)


@router.get("/user_data/summary/admin/{user_id}")
async def api_get_user_summary_admin(
    user_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"])),
):
    return UserService.get_user_summary(user_id, db=db, user_id=user.id)


@router.get("/user_data/summary/user")
async def api_get_user_summary_user(
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin", "user"])),
):
    return UserService.get_user_summary("me", db=db, user_id=user.id)


@router.get("/user_data/word_skills/user")
async def api_get_user_word_skills_user(
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin", "user"])),
):
    return UserService.get_user_word_skills(db=db, user_id=user.id)
