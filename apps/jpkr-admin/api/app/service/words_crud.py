# words_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Any, Optional
from db import SessionLocal, Words
from datetime import datetime


def get_db():
    """데이터베이스 세션을 반환합니다."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_words_batch(words_data: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """
    여러 단어를 한 번에 생성합니다.
    
    Args:
        words_data: 단어 데이터 리스트 [{"word": "단어", "jp_pronunciation": "발음", "kr_pronunciation": "한글발음", "kr_meaning": "의미", "level": 1}]
    
    Returns:
        생성된 단어들의 ID와 데이터를 포함한 딕셔너리 {id: {단어데이터}}
    """
    db = SessionLocal()
    try:
        result = {}
        
        for word_data in words_data:
            # 중복 단어 검사 (word 필드 기준)
            existing_word = db.query(Words).filter(
                Words.word == word_data.get("word")
            ).first()
            
            if existing_word:
                # 중복 단어는 기존 데이터 반환
                result[existing_word.id] = {
                    "word": existing_word.word,
                    "jp_pronunciation": existing_word.jp_pronunciation,
                    "kr_pronunciation": existing_word.kr_pronunciation,
                    "kr_meaning": existing_word.kr_meaning,
                    "level": existing_word.level,
                    "updated_at": existing_word.updated_at,
                    "is_duplicate": True
                }
            else:
                # 새 단어 생성
                new_word = Words(
                    word=word_data.get("word"),
                    jp_pronunciation=word_data.get("jp_pronunciation"),
                    kr_pronunciation=word_data.get("kr_pronunciation"),
                    kr_meaning=word_data.get("kr_meaning"),
                    level=word_data.get("level"),
                    updated_at=datetime.now()
                )
                
                db.add(new_word)
                db.flush()  # ID 생성을 위해 flush
                
                result[new_word.id] = {
                    "word": new_word.word,
                    "jp_pronunciation": new_word.jp_pronunciation,
                    "kr_pronunciation": new_word.kr_pronunciation,
                    "kr_meaning": new_word.kr_meaning,
                    "level": new_word.level,
                    "updated_at": new_word.updated_at,
                    "is_duplicate": False
                }
        
        db.commit()
        return result
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def read_words_batch(word_ids: List[int]) -> Dict[int, Dict[str, Any]]:
    """
    여러 단어를 ID로 조회합니다.
    
    Args:
        word_ids: 조회할 단어 ID 리스트 [1, 2, 3, ...]
    
    Returns:
        조회된 단어들의 ID와 데이터를 포함한 딕셔너리 {id: {단어데이터}}
    """
    db = SessionLocal()
    try:
        words = db.query(Words).filter(Words.id.in_(word_ids)).all()
        
        result = {}
        for word in words:
            result[word.id] = {
                "word": word.word,
                "jp_pronunciation": word.jp_pronunciation,
                "kr_pronunciation": word.kr_pronunciation,
                "kr_meaning": word.kr_meaning,
                "level": word.level,
                "num_examples": str(len(word.examples)),
                "updated_at": word.updated_at
            }
        
        return result
        
    finally:
        db.close()


def update_words_batch(words_data: Dict[int, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """
    여러 단어를 한 번에 업데이트합니다.
    
    Args:
        words_data: 업데이트할 단어 데이터 {id: {단어데이터}}
    
    Returns:
        업데이트된 단어들의 ID와 데이터를 포함한 딕셔너리 {id: {단어데이터}}
    """
    db = SessionLocal()
    try:
        result = {}
        
        for word_id, word_data in words_data.items():
            word = db.query(Words).filter(Words.id == word_id).first()
            
            if word:
                # 단어 데이터 업데이트
                if "word" in word_data:
                    word.word = word_data["word"]
                if "jp_pronunciation" in word_data:
                    word.jp_pronunciation = word_data["jp_pronunciation"]
                if "kr_pronunciation" in word_data:
                    word.kr_pronunciation = word_data["kr_pronunciation"]
                if "kr_meaning" in word_data:
                    word.kr_meaning = word_data["kr_meaning"]
                if "level" in word_data:
                    word.level = word_data["level"]
                
                word.updated_at = datetime.now()
                
                result[word_id] = {
                    "word": word.word,
                    "jp_pronunciation": word.jp_pronunciation,
                    "kr_pronunciation": word.kr_pronunciation,
                    "kr_meaning": word.kr_meaning,
                    "level": word.level,
                    "updated_at": word.updated_at
                }
            else:
                # 해당 ID의 단어가 없는 경우
                result[word_id] = {"error": "Word not found"}
        
        db.commit()
        return result
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def delete_words_batch(word_ids: List[int]) -> Dict[int, str]:
    """
    여러 단어를 ID로 삭제합니다.
    
    Args:
        word_ids: 삭제할 단어 ID 리스트 [1, 2, 3, ...]
    
    Returns:
        삭제 결과를 포함한 딕셔너리 {id: "삭제결과메시지"}
    """
    db = SessionLocal()
    try:
        result = {}
        
        for word_id in word_ids:
            word = db.query(Words).filter(Words.id == word_id).first()
            
            if word:
                db.delete(word)
                result[word_id] = "deleted"
            else:
                result[word_id] = "not found"
        
        db.commit()
        return result
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def search_words_by_word(search_term: str) -> List[Dict[str, Any]]:
    """
    검색어와 일치하는 단어들을 찾습니다 (LIKE 검색).
    
    Args:
        search_term: 검색할 단어 또는 문구
    
    Returns:
        검색된 단어들의 데이터 리스트
    """
    db = SessionLocal()
    try:
        # word, jp_pronunciation, kr_pronunciation, kr_meaning 중 하나라도 일치하는 경우 검색
        search_pattern = f"%{search_term}%"
        
        found_words = db.query(Words).filter(
            or_(
                Words.word.like(search_pattern),
                Words.jp_pronunciation.like(search_pattern),
                Words.kr_pronunciation.like(search_pattern),
                Words.kr_meaning.like(search_pattern)
            )
        ).all()
        
        result = []
        for word in found_words:
            result.append({
                "id": word.id,
                "word": word.word,
                "jp_pronunciation": word.jp_pronunciation,
                "kr_pronunciation": word.kr_pronunciation,
                "kr_meaning": word.kr_meaning,
                "level": word.level,
                "num_examples": str(len(word.examples)),
                "updated_at": word.updated_at
            })
        
        return result
        
    finally:
        db.close()


def get_all_words(limit: Optional[int] = None, offset: Optional[int] = None) -> Dict[str, Any]:
    """
    모든 단어를 조회합니다 (페이지네이션 지원).
    
    Args:
        limit: 조회할 단어 수 제한
        offset: 건너뛸 단어 수
    
    Returns:
        전체 단어 수와 페이지네이션된 단어 데이터를 포함한 딕셔너리
    """
    db = SessionLocal()
    try:
        # 전체 단어 수 조회
        total_count = db.query(Words).count()
        
        # 페이지네이션된 단어 조회
        query = db.query(Words)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        words = query.all()
        
        result_words = []
        for word in words[:100]:
            result_words.append({
                "id": word.id,
                "word": word.word,
                "jp_pronunciation": word.jp_pronunciation,
                "kr_pronunciation": word.kr_pronunciation,
                "kr_meaning": word.kr_meaning,
                "level": word.level,
                "num_examples": str(len(word.examples)),
                "updated_at": word.updated_at
            })
        
        return {
            "total_count": total_count,
            "words": result_words,
            "limit": limit,
            "offset": offset
        }
        
    finally:
        db.close()


def get_random_words(count: int = 50) -> List[Dict[str, Any]]:
    """
    무작위로 지정된 개수의 단어를 조회합니다.
    
    Args:
        count: 조회할 단어 수 (기본값: 50)
    
    Returns:
        무작위로 선택된 단어들의 데이터 리스트
    """
    db = SessionLocal()
    try:
        import random
        
        # 전체 단어 수 조회
        total_count = db.query(Words).count()
        
        if total_count == 0:
            return []
        
        # 무작위로 단어 ID 선택
        all_word_ids = [word.id for word in db.query(Words.id).all()]
        selected_ids = random.sample(all_word_ids, min(count, total_count))
        
        # 선택된 ID로 단어 조회
        words = db.query(Words).filter(Words.id.in_(selected_ids)).all()
        
        result = []
        for word in words:
            # 예문 정보도 함께 가져오기
            examples_list = []
            for example in word.examples:
                examples_list.append({
                    "id": example.id,
                    "word_info": example.word.word,
                    "tags": example.tags,
                    "jp_text": example.jp_text,
                    "kr_meaning": example.kr_meaning,
                    "updated_at": example.updated_at
                })
            
            result.append({
                "word_id": word.id,
                "word": word.word,
                "surface": word.word,  # 퀴즈에서 사용하는 surface 필드
                "jp_pronunciation": word.jp_pronunciation,
                "kr_pronunciation": word.kr_pronunciation,
                "kr_meaning": word.kr_meaning,
                "level": word.level,
                "examples": examples_list,
                "num_examples": len(examples_list),
                "updated_at": word.updated_at
            })
        
        return result
        
    finally:
        db.close()
