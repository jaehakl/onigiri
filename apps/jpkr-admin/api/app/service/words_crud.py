# words_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, select, delete
from typing import List, Dict, Any, Optional, Sequence
from sqlalchemy.dialects.postgresql import insert as pg_insert

from models import WordData
from db import SessionLocal, Word
from datetime import datetime

def row_to_dict(obj) -> dict:
    # ORM 객체를 dict로 안전하게 변환
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def update_words_batch(words_data: List[Dict[str, Any]], db: Session=None, user_id:str = None) -> Dict[int, Dict[str, Any]]:
    result = {}        
    for word_data in words_data:
        word = db.query(Word).filter(Word.id == word_data.id).first()
        
        if word:
            # 단어 데이터 업데이트
            word.word = word_data.word
            word.jp_pronunciation = word_data.jp_pronunciation
            word.kr_pronunciation = word_data.kr_pronunciation
            word.kr_meaning = word_data.kr_meaning
            word.level = word_data.level
            word.user_id = user_id
            
            result[word_data.id] = row_to_dict(word)            
        else:
            # 해당 ID의 단어가 없는 경우
            result[word_data.id] = {"error": "Word not found"}    
    db.commit()
    return result
        

def delete_words_batch(word_ids: Sequence[str], db: Session, user_id: str) -> Dict[int, str]:
    if not word_ids:
        return {}
    ids = set(str(wid) for wid in word_ids)
    stmt = (
        delete(Word)
        .where(Word.id.in_(ids), Word.user_id == user_id)
        .returning(Word.id)
    )
    deleted_ids = set(db.execute(stmt).scalars().all())
    db.commit()
    return {wid: ("deleted" if wid in deleted_ids else "not found") for wid in word_ids}
