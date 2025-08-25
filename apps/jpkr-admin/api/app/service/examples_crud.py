# examples_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Any, Optional
from db import SessionLocal, Examples
from datetime import datetime


def get_db():
    """데이터베이스 세션을 반환합니다."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_examples_batch(examples_data: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """
    여러 예문을 한 번에 생성합니다.
    
    Args:
        examples_data: 예문 데이터 리스트 [{"word_id": 1, "tags": "태그", "jp_text": "일본어텍스트", "kr_meaning": "한국어의미"}]
    
    Returns:
        생성된 예문들의 ID와 데이터를 포함한 딕셔너리 {id: {예문데이터}}
    """
    db = SessionLocal()
    try:
        result = {}
        
        for example_data in examples_data:
            # 새 예문 생성
            new_example = Examples(
                word_id=example_data.get("word_id"),
                tags=example_data.get("tags"),
                jp_text=example_data.get("jp_text"),
                kr_meaning=example_data.get("kr_meaning"),
                updated_at=datetime.now()
            )
            
            db.add(new_example)
            db.flush()  # ID 생성을 위해 flush
            
            result[new_example.id] = {
                "word_id": new_example.word_id,
                "tags": new_example.tags,
                "jp_text": new_example.jp_text,
                "kr_meaning": new_example.kr_meaning,
                "updated_at": new_example.updated_at
            }
        
        db.commit()
        return result
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def read_examples_batch(example_ids: List[int]) -> Dict[int, Dict[str, Any]]:
    """
    여러 예문을 ID로 조회합니다.
    
    Args:
        example_ids: 조회할 예문 ID 리스트 [1, 2, 3, ...]
    
    Returns:
        조회된 예문들의 ID와 데이터를 포함한 딕셔너리 {id: {예문데이터}}
    """
    db = SessionLocal()
    try:
        examples = db.query(Examples).filter(Examples.id.in_(example_ids)).all()
        
        result = {}
        for example in examples:
            result[example.id] = {
                "word_id": example.word_id,
                "word_info": example.word.word,
                "tags": example.tags,
                "jp_text": example.jp_text,
                "kr_meaning": example.kr_meaning,
                "updated_at": example.updated_at
            }
        
        return result
        
    finally:
        db.close()


def update_examples_batch(examples_data: Dict[int, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """
    여러 예문을 한 번에 업데이트합니다.
    
    Args:
        examples_data: 업데이트할 예문 데이터 {id: {예문데이터}}
    
    Returns:
        업데이트된 예문들의 ID와 데이터를 포함한 딕셔너리 {id: {예문데이터}}
    """
    db = SessionLocal()
    try:
        result = {}
        
        for example_data in examples_data:
            example_id = example_data["id"]
            example = db.query(Examples).filter(Examples.id == example_id).first()
            
            if example:
                # 예문 데이터 업데이트
                if "tags" in example_data:
                    example.tags = example_data["tags"]
                if "jp_text" in example_data:
                    example.jp_text = example_data["jp_text"]
                if "kr_meaning" in example_data:
                    example.kr_meaning = example_data["kr_meaning"]
                
                example.updated_at = datetime.now()
                
                result[example_id] = {
                    "word_id": example.word_id,
                    "tags": example.tags,
                    "jp_text": example.jp_text,
                    "kr_meaning": example.kr_meaning,
                    "updated_at": example.updated_at
                }
            else:
                # 해당 ID의 예문이 없는 경우
                result[example_id] = {"error": "Example not found"}
        
        db.commit()
        return result
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def delete_examples_batch(example_ids: List[int]) -> Dict[int, str]:
    """
    여러 예문을 ID로 삭제합니다.
    
    Args:
        example_ids: 삭제할 예문 ID 리스트 [1, 2, 3, ...]
    
    Returns:
        삭제 결과를 포함한 딕셔너리 {id: "삭제결과메시지"}
    """
    db = SessionLocal()
    try:
        result = {}
        
        for example_id in example_ids:
            example = db.query(Examples).filter(Examples.id == example_id).first()
            
            if example:
                db.delete(example)
                result[example_id] = "deleted"
            else:
                result[example_id] = "not found"
        
        db.commit()
        return result
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def search_examples_by_text(search_term: str) -> List[Dict[str, Any]]:
    """
    검색어와 일치하는 예문들을 찾습니다 (LIKE 검색).
    
    Args:
        search_term: 검색할 텍스트 또는 문구
    
    Returns:
        검색된 예문들의 데이터 리스트
    """
    db = SessionLocal()
    try:
        # jp_text, kr_meaning, tags 중 하나라도 일치하는 경우 검색
        search_pattern = f"%{search_term}%"
        
        found_examples = db.query(Examples).filter(
            or_(
                Examples.jp_text.like(search_pattern),
                Examples.kr_meaning.like(search_pattern),
                Examples.tags.like(search_pattern)
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
                "updated_at": example.updated_at
            })
        
        return result
        
    finally:
        db.close()


def get_examples_by_word_id(word_id: int) -> List[Dict[str, Any]]:
    """
    특정 단어 ID에 해당하는 모든 예문을 조회합니다.
    
    Args:
        word_id: 조회할 단어 ID
    
    Returns:
        해당 단어의 예문 데이터 리스트
    """
    db = SessionLocal()
    try:
        examples = db.query(Examples).filter(Examples.word_id == word_id).all()
        
        result = []
        for example in examples:
            result.append({
                "id": example.id,
                "word_id": example.word_id,
                "word_info": example.word.word,
                "tags": example.tags,
                "jp_text": example.jp_text,
                "kr_meaning": example.kr_meaning,
                "updated_at": example.updated_at
            })
        
        return result
        
    finally:
        db.close()


def get_all_examples(limit: Optional[int] = None, offset: Optional[int] = None) -> Dict[str, Any]:
    """
    모든 예문을 조회합니다 (페이지네이션 지원).
    
    Args:
        limit: 조회할 예문 수 제한
        offset: 건너뛸 예문 수
    
    Returns:
        전체 예문 수와 페이지네이션된 예문 데이터를 포함한 딕셔너리
    """
    db = SessionLocal()
    try:
        # 전체 예문 수 조회
        total_count = db.query(Examples).count()
        
        # 페이지네이션된 예문 조회
        query = db.query(Examples)
        
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
                "updated_at": example.updated_at
            })
        
        return {
            "total_count": total_count,
            "examples": result_examples,
            "limit": limit,
            "offset": offset
        }
        
    finally:
        db.close()


