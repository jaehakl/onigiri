from typing import List, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
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

    words_map = {}
    for word_data in data:
        words_map[word_data['word']] = word_data

    stmt = (
        select(Word)
        .options(selectinload(Word.examples), selectinload(Word.user_word_skills))
        .where(Word.word.in_(list(words_map.keys())))
    )
    words_existing = db.execute(stmt).scalars().all()
    words_existing_map = {w.word: w for w in words_existing}

    # 이후는 words 를 바탕으로 같은 방식으로 매칭
    for word in words_map.keys():
        if word not in words_existing_map:
            new_word = Word(
                user_id=user_id,
                word=word,
                jp_pronunciation=words_map[word]['jp_pronunciation'],
                kr_pronunciation=words_map[word]['kr_pronunciation'],
                kr_meaning=words_map[word]['kr_meaning'],
                level=words_map[word]['level']
            )
            db.add(new_word)
            created_words.append(word)
            db.flush()
            new_word_id = new_word.id
        elif words_existing_map[word].user_id == user_id:
            # 기존 단어 업데이트
            words_existing_map[word].jp_pronunciation = words_map[word]['jp_pronunciation']
            words_existing_map[word].kr_pronunciation = words_map[word]['kr_pronunciation']
            words_existing_map[word].kr_meaning = words_map[word]['kr_meaning']
            words_existing_map[word].level = words_map[word]['level']
            updated_words.append(words_existing_map[word].word)
            new_word_id = words_existing_map[word].id
        else:
            new_word = Word(
                user_id=user_id,
                root_word_id=words_existing_map[word].id,
                word=word,
                jp_pronunciation=words_map[word]['jp_pronunciation'],
                kr_pronunciation=words_map[word]['kr_pronunciation'],
                kr_meaning=words_map[word]['kr_meaning'],
                level=words_map[word]['level']
            )
            db.add(new_word)
            created_words.append(word)
            db.flush()
            new_word_id = new_word.id
        if new_word_id:
            existing_skill = db.query(UserWordSkill).filter(
                UserWordSkill.user_id == user_id,
                UserWordSkill.word_id == new_word_id
            ).first()
            if existing_skill:
                # 기존 스킬 업데이트
                for skill_key in ['skill_kanji', 'skill_word_reading', 'skill_word_speaking', 'skill_sentence_reading', 'skill_sentence_speaking', 'skill_sentence_listening']:
                    if skill_key in words_map[word]:
                        setattr(existing_skill, skill_key, words_map[word][skill_key])
                        updated_skills.append(word)
            else:
                # 새로운 스킬 생성
                new_skill = UserWordSkill(
                    user_id=user_id,
                    word_id=new_word_id,
                    skill_kanji=words_map[word].get('skill_kanji', 0),
                    skill_word_reading=words_map[word].get('skill_word_reading', 0),
                    skill_word_speaking=words_map[word].get('skill_word_speaking', 0),
                    skill_sentence_reading=words_map[word].get('skill_sentence_reading', 0),
                    skill_sentence_speaking=words_map[word].get('skill_sentence_speaking', 0),
                    skill_sentence_listening=words_map[word].get('skill_sentence_listening', 0),
                    is_favorite=False
                )
                db.add(new_skill)
                created_skills.append(word)
                db.flush()
    db.commit()
    response = {
        "success": True,
        "message": "Words processed successfully",
        "created_words": created_words,
        "updated_words": updated_words,
        "created_skills": created_skills,
        "updated_skills": updated_skills,
    }
    return response
