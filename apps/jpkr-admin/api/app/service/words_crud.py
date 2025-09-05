# words_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import delete
from typing import List, Dict, Any, Sequence

from db import Word

def row_to_dict(obj) -> dict:
    # ORM 객체를 dict로 안전하게 변환
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def update_words_batch(words_data: List[Dict[int, Any]], db: Session=None, user_id:str = None) -> Dict[int, Dict[str, Any]]:
    result = {}        
    for word_data in words_data:
        print(word_data)
        word = db.query(Word).filter(Word.id == word_data.id).first()
        
        if word:
            # 단어 데이터 업데이트
            word.lemma = word_data.lemma
            word.jp_pron = word_data.jp_pron
            word.kr_pron = word_data.kr_pron
            word.kr_mean = word_data.kr_mean
            word.level = word_data.level
            word.user_id = user_id            
            result[word_data.id] = row_to_dict(word)            
        else:
            # 해당 ID의 단어가 없는 경우
            result[word_data.id] = {"error": "Word not found"}    
    db.commit()
    return result
        

def delete_words_batch(word_ids: Sequence[int], db: Session, user_id: str) -> Dict[int, str]:
    if not word_ids:
        return {}
    ids = set(int(wid) for wid in word_ids)
    stmt = (
        delete(Word)
        .where(Word.id.in_(ids))
        .returning(Word.id)
    )
    deleted_ids = set(db.execute(stmt).scalars().all())
    db.commit()
    return {wid: ("deleted" if wid in deleted_ids else "not found") for wid in word_ids}
