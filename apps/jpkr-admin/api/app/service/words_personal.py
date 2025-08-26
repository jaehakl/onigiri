from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request
import uuid
from db import Word, UserWordSkill

def create_words_personal(data: List[Dict[str, Any]], db: Session, user_id: str):
    """
    사용자 개인 단어 데이터를 처리하여 Word 및 UserWordSkill 테이블을 업데이트합니다.
    
    Args:
        data: 단어 데이터 리스트
        db: 데이터베이스 세션
        user_id: 사용자 ID
    
    Returns:
        처리 결과 메시지
    """
    created_words = []
    updated_words = []
    created_skills = []
    updated_skills = []
    
    for word_data in data:
        original_word = word_data.get('originalWord', {})
        original_word_id = original_word.get('word_id')
        
        if original_word_id is None:
            # 새로운 단어 생성
            new_word = Word(
                id=str(uuid.uuid4()),
                user_id=user_id,
                word=word_data['word'],
                jp_pronunciation=word_data['jp_pronunciation'],
                kr_pronunciation=word_data['kr_pronunciation'],
                kr_meaning=word_data['kr_meaning'],
                level=word_data['level']
            )
            db.add(new_word)
            db.flush()  # ID 생성을 위해 flush
            
            # 새로운 UserWordSkill 생성
            new_skill = UserWordSkill(
                id=str(uuid.uuid4()),
                user_id=user_id,
                word_id=new_word.id,
                skill_kanji=word_data.get('skill_kanji', 0),
                skill_word_reading=word_data.get('skill_word_reading', 0),
                skill_word_speaking=word_data.get('skill_word_speaking', 0),
                skill_sentence_reading=word_data.get('skill_sentence_reading', 0),
                skill_sentence_speaking=word_data.get('skill_sentence_speaking', 0),
                skill_sentence_listening=word_data.get('skill_sentence_listening', 0),
                is_favorite=False
            )
            db.add(new_skill)
            
            created_words.append(new_word.word)
            created_skills.append(new_word.word)
            
        else:
            # 기존 단어 업데이트
            existing_word = db.query(Word).filter(Word.id == original_word_id).first()
            if existing_word:
                existing_word.word = word_data['word']
                existing_word.jp_pronunciation = word_data['jp_pronunciation']
                existing_word.kr_pronunciation = word_data['kr_pronunciation']
                existing_word.kr_meaning = word_data['kr_meaning']
                existing_word.level = word_data['level']
                
                updated_words.append(existing_word.word)
                
                # UserWordSkill 처리
                existing_skill = db.query(UserWordSkill).filter(
                    UserWordSkill.user_id == user_id,
                    UserWordSkill.word_id == original_word_id
                ).first()
                
                if existing_skill:
                    # 기존 스킬 업데이트
                    for skill_key in ['skill_kanji', 'skill_word_reading', 'skill_word_speaking', 'skill_sentence_reading', 'skill_sentence_speaking', 'skill_sentence_listening']:
                        if skill_key in word_data:
                            setattr(existing_skill, skill_key, word_data[skill_key])
                            updated_skills.append(existing_word.word)
                else:
                    # 새로운 스킬 생성
                    new_skill = UserWordSkill(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        word_id=original_word_id,
                        skill_kanji=word_data.get('skill_kanji', 0),
                        skill_word_reading=word_data.get('skill_word_reading', 0),
                        skill_word_speaking=word_data.get('skill_word_speaking', 0),
                        skill_sentence_reading=word_data.get('skill_sentence_reading', 0),
                        skill_sentence_speaking=word_data.get('skill_sentence_speaking', 0),
                        skill_sentence_listening=word_data.get('skill_sentence_listening', 0),
                        is_favorite=word_data.get('is_favorite', False)
                    )
                    db.add(new_skill)
                    created_skills.append(existing_word.word)
        
    try:
        db.commit()
        response = {
            "success": True,
            "message": "Words processed successfully",
            "created_words": len(created_words),
            "updated_words": len(updated_words),
            "created_skills": len(created_skills),
            "updated_skills": len(updated_skills),
        }
        return response
    except Exception as e:
        db.rollback()
        response = {
            "success": False,
            "message": f"Error processing words: {str(e)}"
        }
        return response