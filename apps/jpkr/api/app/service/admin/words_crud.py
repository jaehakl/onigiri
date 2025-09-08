# words_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, select, delete, func, case
from typing import List, Dict, Any, Optional, Sequence
from sqlalchemy.dialects.postgresql import insert as pg_insert

from models import WordData
from db import Word

def row_to_dict(obj) -> dict:
    # ORM 객체를 dict로 안전하게 변환
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def update_words_batch(words_data: List[Dict[str, Any]], db: Session=None, user_id:str = None) -> Dict[int, Dict[str, Any]]:
    result = {}        
    for word_data in words_data:
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
    ids = set(wid for wid in word_ids)
    stmt = (
        delete(Word)
        .where(Word.id.in_(ids), Word.user_id == user_id)
        .returning(Word.id)
    )
    deleted_ids = set(db.execute(stmt).scalars().all())
    db.commit()
    return {wid: ("deleted" if wid in deleted_ids else "not found") for wid in word_ids}


def search_words_by_word(search_term: str, db: Session=None, user_id:str = None) -> List[Dict[str, Any]]:
    search_terms = search_term.split(',')
    hangul_pattern = f"%{search_terms[0]}%"
    hiragana_pattern = f"%{search_terms[1]}%"
    
    # 필요한 필드만 선택하여 쿼리 최적화 (embedding 제외)
    query = db.query(
        Word.id,
        Word.lemma_id,
        Word.lemma,
        Word.jp_pron,
        Word.kr_pron,
        Word.kr_mean,
        Word.level,
        Word.created_at,
        Word.updated_at,
        # embedding 존재 여부만 확인 (실제 값은 가져오지 않음)
        case(
            (Word.embedding.isnot(None), 1),
            else_=0
        ).label('has_embedding')
    ).filter(
        or_(
            Word.lemma.like(hiragana_pattern),
            Word.jp_pron.like(hiragana_pattern),
            Word.kr_pron.like(hangul_pattern),
            Word.kr_mean.like(hangul_pattern),
        )
    )
    
    found_words = query.all()
    
    # 예문 수를 가져오기 위한 별도 쿼리
    word_ids = [row.id for row in found_words]
    example_counts = {}
    if word_ids:
        from db import WordExample
        example_count_query = db.query(
            WordExample.word_id,
            func.count(WordExample.example_id).label('example_count')
        ).filter(WordExample.word_id.in_(word_ids)).group_by(WordExample.word_id)
        
        for row in example_count_query.all():
            example_counts[row.word_id] = row.example_count
    
    result = []
    for word in found_words:
        word_data = {
            "id": word.id,
            "lemma_id": word.lemma_id,
            "lemma": word.lemma,
            "jp_pron": word.jp_pron,
            "kr_pron": word.kr_pron,
            "kr_mean": word.kr_mean,
            "level": word.level,
            "num_examples": example_counts.get(word.id, 0),
            "has_embedding": word.has_embedding,
            "created_at": word.created_at,
            "updated_at": word.updated_at
        }
        result.append(word_data)
    return result
        

def get_all_words(limit: Optional[int] = None, offset: Optional[int] = None, db: Session=None, user_id:str = None) -> Dict[str, Any]:
    total_count = db.query(Word).count()    

    # 필요한 필드만 선택하여 쿼리 최적화 (embedding 제외)
    query = db.query(
        Word.id,
        Word.lemma_id,
        Word.lemma,
        Word.jp_pron,
        Word.kr_pron,
        Word.kr_mean,
        Word.level,
        # embedding 존재 여부만 확인 (실제 값은 가져오지 않음)
        case(
            (Word.embedding.isnot(None), 1),
            else_=0
        ).label('has_embedding')
    )
    
    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)
    
    words = query.all()
    
    # 예문 수를 가져오기 위한 별도 쿼리
    word_ids = [row.id for row in words]
    example_counts = {}
    if word_ids:
        from db import WordExample
        example_count_query = db.query(
            WordExample.word_id,
            func.count(WordExample.example_id).label('example_count')
        ).filter(WordExample.word_id.in_(word_ids)).group_by(WordExample.word_id)
        
        for row in example_count_query.all():
            example_counts[row.word_id] = row.example_count
    
    result_words = []
    for word in words:
        result_words.append({
            "id": word.id,
            "lemma_id": word.lemma_id,
            "lemma": word.lemma,
            "jp_pron": word.jp_pron,
            "kr_pron": word.kr_pron,
            "kr_mean": word.kr_mean,
            "level": word.level,
            "num_examples": example_counts.get(word.id, 0),
            "has_embedding": word.has_embedding
        })
    
    return {
        "total_count": total_count,
        "words": result_words,
        "limit": limit,
        "offset": offset
    }
    