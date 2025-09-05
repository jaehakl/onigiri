# words_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, select, delete
from typing import List, Dict, Any, Optional, Sequence
from sqlalchemy.dialects.postgresql import insert as pg_insert

from models import TextData
from db import SessionLocal, UserText
from datetime import datetime


def row_to_dict(obj) -> dict:
    # ORM 객체를 dict로 안전하게 변환
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

async def create_user_text(user_text_data: TextData, db: Session, user_id: Optional[str] = None) -> Dict[str, dict]:
    if not user_text_data:
        return {}
    user_text = UserText(
        title=user_text_data.title,
        text=user_text_data.text,
        tags=user_text_data.tags,
        youtube_url=user_text_data.youtube_url,
        user_id=user_id,
    )
    db.add(user_text)
    db.commit()
    return row_to_dict(user_text)

async def get_user_text(user_text_id: int, db: Session, user_id: str) -> TextData:
    stmt = select(UserText).filter(UserText.id == user_text_id)
    user_text = db.execute(stmt).scalar_one_or_none()

    if user_text:
        return {
            'id': user_text.id,
            'title': user_text.title,
            'text': user_text.text,
            'tags': user_text.tags,
            'youtube_url': user_text.youtube_url,
            'audio_url': user_text.audio_url,
            'created_at': user_text.created_at,
            'updated_at': user_text.updated_at
        }
    else:
        return None

async def get_user_text_list(limit, offset, db: Session = None, user_id: str = None) -> Dict[str, Any]:
    total_count = db.query(UserText).filter(UserText.user_id == user_id).count()
    stmt = select(UserText.id, UserText.title, UserText.tags).filter(UserText.user_id == user_id)
    if limit:
        stmt = stmt.limit(limit)
    if offset:
        stmt = stmt.offset(offset)
    user_texts = db.execute(stmt).all()
    result = {
        "total_count": total_count,
        "user_texts": [{'id': user_text.id, 'title': user_text.title, 'tags': user_text.tags} for user_text in user_texts],
        "limit": limit,
        "offset": offset
    }
    return result

async def update_user_text(user_text_data: TextData, db: Session=None, user_id:str = None) -> Dict[int, Dict[str, Any]]:
    result = {}        
    stmt = select(UserText).filter(UserText.id == user_text_data.id)
    user_text = db.execute(stmt).scalar_one_or_none()
    if user_text:
        for key, value in user_text_data.model_dump().items():
            if value and key != "id":
                setattr(user_text, key, value)
        user_text.user_id = user_id
        result[user_text_data.id] = row_to_dict(user_text)            
        db.commit()
    else:        
        result[user_text_data.id] = create_user_text(user_text_data, db, user_id)
    return result        

async def delete_user_text(user_text_id: int, db: Session, user_id: str) -> Dict[int, str]:
    if not user_text_id:
        return {}
    db.query(UserText).filter(UserText.id == user_text_id).delete()
    db.commit()
    return "deleted"