from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
import uuid

from db import Word, WordExample, UserWordSkill


def merge_duplicated_words(
    word_ids: List[int],
    new_word_data: Dict[str, Any],
    db: Session,
    user_id: str
) -> Dict[str, Any]:
    """
    여러 Word id 목록과 하나의 word data를 입력받아 중복된 단어들을 병합합니다.
    
    Args:
        db: 데이터베이스 세션
        word_ids: 병합할 기존 단어들의 ID 목록
        new_word_data: 새로운 단어 데이터 (word, jp_pronunciation, kr_pronunciation, kr_meaning, level)
    
    Returns:
        병합 결과 정보
    """
    
    if not word_ids:
        raise ValueError("word_ids 목록이 비어있습니다.")
    
    if len(word_ids) < 2:
        raise ValueError("병합하려면 최소 2개 이상의 단어 ID가 필요합니다.")
    
    # 새로운 단어 생성
    new_word = Word(
        user_id=user_id,
        lemma_id=new_word_data["lemma_id"],
        lemma=new_word_data["lemma"],
        jp_pron=new_word_data["jp_pron"],
        kr_pron=new_word_data["kr_pron"],
        kr_mean=new_word_data["kr_mean"],
        level=new_word_data["level"]
    )
    
    # 새 단어를 데이터베이스에 추가
    db.add(new_word)
    db.flush()  # ID 생성을 위해 flush
    
    # 기존 단어들의 관련 데이터를 새 단어로 연결
    for word_id in word_ids:
        # 기존 단어 조회
        existing_word = db.query(Word).filter(Word.id == word_id).first()
        if not existing_word:
            continue
        
        # 1. WordExample 연결
        word_examples = db.query(WordExample).filter(WordExample.word_id == word_id).all()
        for word_example in word_examples:
            word_example.word_id = new_word.id
                
        # 2. UserWordSkill 연결
        user_word_skills = db.query(UserWordSkill).filter(UserWordSkill.word_id == word_id).all()
        for user_word_skill in user_word_skills:
            user_word_skill.word_id = new_word.id
                    
    # 기존 단어들 삭제
    for word_id in word_ids:
        existing_word = db.query(Word).filter(Word.id == word_id).first()
        if existing_word:
            db.delete(existing_word)
    
    # 변경사항 커밋
    db.commit()
    
    return {
        "success": True,
        "new_word_id": new_word.id,
        "merged_word_count": len(word_ids),
        "message": f"{len(word_ids)}개의 단어가 성공적으로 병합되었습니다."
    }
