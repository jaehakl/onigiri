from typing import List, Dict, Any

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from models import WordUpdate, WordFilterData
from service.admin.words_crud import (
    update_words_batch,
    delete_words_batch,
    get_all_words,
    search_words_by_word,
)
from service.admin.filter_words import filter_words_by_criteria
from service.words_personal import create_words_personal, get_random_words_to_learn
from user_auth.routes import get_db
from user_auth.utils.auth_wrapper import require_roles

router = APIRouter(prefix="/words", tags=["words"])


@router.post("/update/batch")
async def api_update_words(
    words_data: List[WordUpdate],
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"])),
):
    return update_words_batch(words_data, db=db, user_id=user.id)


@router.post("/delete/batch")
async def api_delete_words(
    word_ids: List[int],
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"])),
):
    return delete_words_batch(word_ids, db=db, user_id=user.id)


@router.post("/all")
async def api_get_words(
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"])),
):
    limit = data.get("limit")
    offset = data.get("offset")
    return get_all_words(limit, offset, db=db, user_id=user.id)


@router.get("/search/{search_term}")
async def api_search_word(
    search_term: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin", "user"])),
):
    return search_words_by_word(search_term, db=db, user_id=user.id)


@router.post("/create/personal")
async def api_create_words_personal(
    data_json: str = Form(...),
    file_meta_json: str = Form("[]"),
    files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin", "user"])),
):
    # files are handled via Form/File in the service; keep signature consistent
    return await create_words_personal(
        data_json, file_meta_json, files, db=db, user_id=user.id
    )


@router.get("/personal/random/{limit}")
async def api_get_random_words_to_learn(
    limit: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin", "user"])),
):
    return get_random_words_to_learn(limit, db=db, user_id=user.id)


@router.post("/filter")
async def api_filter_words(
    word_filter_data: WordFilterData,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"])),
):
    return filter_words_by_criteria(
        db=db, user_id=user.id, **word_filter_data.model_dump()
    )
