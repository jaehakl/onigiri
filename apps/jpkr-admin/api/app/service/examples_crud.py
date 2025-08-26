# examples_crud.py
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, select
from typing import List, Dict, Any, Optional
from db import SessionLocal, Example
from models import ExampleData
from sqlalchemy.orm import selectinload


def get_db():
    """데이터베이스 세션을 반환합니다."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_examples_batch(examples_data: List[ExampleData], db: Session=None, user_id:str = None):
    """
    여러 예문을 한 번에 생성합니다.
    Args:
        examples_data: 예문 데이터 리스트 [ExampleData]    
    """
    if db is None:
        db = SessionLocal()
    try:
        for example_data in examples_data:
            new_example = Example(
                word_id=example_data.word_id,
                tags=example_data.tags,
                jp_text=example_data.jp_text,
                kr_meaning=example_data.kr_meaning,
                user_id=user_id
            )            
            db.add(new_example)
            db.flush()  # ID 생성을 위해 flush                
        db.commit()
        return
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def update_examples_batch(examples_data: List[ExampleData], db: Session=None, user_id:str = None):
    """
    여러 예문을 한 번에 업데이트합니다.
    
    Args:
        examples_data: 업데이트할 예문 데이터 [ExampleData]
    """
    if db is None:
        db = SessionLocal()
    try:
        for example_data in examples_data:
            example = db.query(Example).filter(Example.id == example_data.id).first()            
            if example:
                # 예문 데이터 업데이트
                example.word_id = example_data.word_id
                example.tags = example_data.tags
                example.jp_text = example_data.jp_text
                example.kr_meaning = example_data.kr_meaning
                example.user_id = user_id
            else:
                # 해당 ID의 예문이 없는 경우
                raise Exception("Example not found")        
        db.commit()
        return
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def delete_examples_batch(example_ids: List[int], db: Session=None, user_id:str = None):
    """
    여러 예문을 ID로 일괄 삭제합니다.
    
    Args:
        example_ids: 삭제할 예문 ID 리스트 [1, 2, 3, ...]
    
    Returns:
        삭제된 예문 수
    """
    if db is None:
        db = SessionLocal()
    try:
        deleted_count = db.query(Example).filter(Example.id.in_(example_ids)).delete(synchronize_session=False)
        db.commit()
        print(f"총 {deleted_count}개의 예문을 일괄 삭제했습니다.")
        return deleted_count                
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def search_examples_by_text(search_term: str, db: Session=None, user_id:str = None) -> List[Dict[str, Any]]:
    """
    검색어와 일치하는 예문들을 찾습니다 (LIKE 검색).
    
    Args:
        search_term: 검색할 텍스트 또는 문구
    
    Returns:
        검색된 예문들의 데이터 리스트
    """
    if db is None:
        db = SessionLocal()
    try:
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
            result.append({
                "id": example.id,
                "word_id": example.word_id,
                "word_info": example.word.word,
                "tags": example.tags,
                "jp_text": example.jp_text,
                "kr_meaning": example.kr_meaning,
            })
        
        return result
        
    finally:
        db.close()


def get_examples_by_word_id(word_id: int, db: Session=None, user_id:str = None) -> List[Dict[str, Any]]:
    """
    특정 단어 ID에 해당하는 모든 예문을 조회합니다.
    
    Args:
        word_id: 조회할 단어 ID
    
    Returns:
        해당 단어의 예문 데이터 리스트
    """
    if db is None:
        db = SessionLocal()
    try:
        examples = db.query(Example).filter(Example.word_id == word_id).all()
        
        result = []
        for example in examples:
            result.append({
                "id": example.id,
                "word_id": example.word_id,
                "word_info": example.word.word,
                "tags": example.tags,
                "jp_text": example.jp_text,
                "kr_meaning": example.kr_meaning,
            })
        
        return result
        
    finally:
        db.close()


def get_all_examples(limit: Optional[int] = None, offset: Optional[int] = None, db: Session=None, user_id:str = None) -> Dict[str, Any]:
    """
    모든 예문을 조회합니다 (페이지네이션 지원).
    
    Args:
        limit: 조회할 예문 수 제한
        offset: 건너뛸 예문 수
    
    Returns:
        전체 예문 수와 페이지네이션된 예문 데이터를 포함한 딕셔너리
    """
    if db is None:
        db = SessionLocal()
    try:
        # 전체 예문 수 조회
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
                "word_id": example.word_id,
                "word_info": example.word.word,
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
        
    finally:
        db.close()


