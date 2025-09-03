# examples_crud.py
from datetime import datetime
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, select, case
from collections import defaultdict
from typing import List, Dict, Any, Optional
from db import SessionLocal, Example, WordExample, Word
from models import ExampleData
from fugashi import Tagger

def row_to_dict(obj) -> dict:
    # ORM 객체를 dict로 안전하게 변환
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def create_examples_batch(examples_data: List[ExampleData], db: Session=None, user_id:str = None):
    for example_data in examples_data:
        new_example = Example(
            tags=example_data.tags,
            jp_text=example_data.jp_text,
            kr_meaning=example_data.kr_meaning,
            user_id=user_id
        )            
        db.add(new_example)
        db.flush()  # ID 생성을 위해 flush                
        new_word_example = WordExample(
            word_id=example_data.word_id,
            example_id=new_example.id
        )
        db.add(new_word_example)
        db.flush()
    db.commit()
    return


def update_examples_batch(examples_data: List[ExampleData], db: Session=None, user_id:str = None):
    for example_data in examples_data:
        example = db.query(Example).filter(Example.id == example_data.id).first()            
        if example:
            # 예문 데이터 업데이트
            example.tags = example_data.tags
            example.jp_text = example_data.jp_text
            example.kr_meaning = example_data.kr_meaning
            example.user_id = user_id
        else:
            # 해당 ID의 예문이 없는 경우
            raise Exception("Example not found")        
    db.commit()
    return
        

def delete_examples_batch(example_ids: List[int], db: Session=None, user_id:str = None):
    deleted_count = db.query(Example).filter(Example.id.in_(example_ids)).delete(synchronize_session=False)
    db.commit()
    print(f"총 {deleted_count}개의 예문을 일괄 삭제했습니다.")
    return deleted_count                


def search_examples_by_text(search_term: str, db: Session=None, user_id:str = None) -> List[Dict[str, Any]]:
    # jp_text, kr_meaning, tags 중 하나라도 일치하는 경우 검색
    search_pattern = f"%{search_term}%"
    
    found_examples = db.query(Example).filter(
        or_(
            Example.jp_text.like(search_pattern),
            Example.kr_meaning.like(search_pattern),
            Example.tags.like(search_pattern)
        )
    ).all()
    
    result = []
    for example in found_examples:
        word_example = db.query(WordExample).filter(WordExample.example_id == example.id).first()
        if word_example:
            word_id = word_example.word_id
            word_info = db.query(Word).filter(Word.id == word_id).first()
        else:
            word_id = None
            word_info = None
        result.append({
            "id": example.id,
            "word_id": word_id,
            "word_info": word_info.word,
            "tags": example.tags,
            "jp_text": example.jp_text,
            "kr_meaning": example.kr_meaning,
        })
    
    return result
        

def get_examples_by_word_id(word_id: int, db: Session=None, user_id:str = None) -> List[Dict[str, Any]]:
    word_examples = db.query(WordExample).filter(WordExample.word_id == word_id).all()
    result = []
    for word_example in word_examples:
        result.append({
            "id": word_example.example_id,
            "word_id": word_example.word_id,
            "word_info": word_example.word.word,
            "tags": word_example.example.tags,
            "jp_text": word_example.example.jp_text,
            "kr_meaning": word_example.example.kr_meaning,
        })
    return result
        

def get_all_examples(limit: Optional[int] = None, offset: Optional[int] = None, db: Session=None, user_id:str = None) -> Dict[str, Any]:
    total_count = db.query(Example).count()

    query = db.query(Example)
    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)
    examples = query.all()

    result_examples = []
    for example in examples:
        result_examples.append({
            "id": example.id,
            "word_id": example.word_examples[0].word_id,
            "word_info": example.word_examples[0].word.word,
            "tags": example.tags,
            "jp_text": example.jp_text,
            "kr_meaning": example.kr_meaning,
        })
    
    return {
        "total_count": total_count,
        "examples": result_examples,
        "limit": limit,
        "offset": offset
    }


