from typing import List, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, case
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

def get_random_words_to_learn(limit: int, db: Session, user_id: str):
    """
    사용자가 학습할 단어들을 우선순위에 따라 가져옵니다.
    
    우선순위:
    1. level: N5 > N4 > N3 > N2 > N1 > 레벨 null 순
    2. 같은 level인 경우 사용자의 user word skill 총합이 작은 순
    3. 2가 같은 경우, 무작위 선택
    
    Args:
        limit: 가져올 단어 수
        db: 데이터베이스 세션
        user_id: 사용자 ID
    
    Returns:
        우선순위에 따라 정렬된 단어 리스트
    """
    # level 우선순위를 위한 case 문
    level_priority = case(
        (Word.level == 'N5', 1),
        (Word.level == 'N4', 2),
        (Word.level == 'N3', 3),
        (Word.level == 'N2', 4),
        (Word.level == 'N1', 5),
        else_=6
    )
    
    # UserWordSkill의 총합을 계산 (없는 경우 0으로 처리)
    skill_sum = func.coalesce(
        func.coalesce(UserWordSkill.skill_kanji, 0) +
        func.coalesce(UserWordSkill.skill_word_reading, 0) +
        func.coalesce(UserWordSkill.skill_word_speaking, 0) +
        func.coalesce(UserWordSkill.skill_sentence_reading, 0) +
        func.coalesce(UserWordSkill.skill_sentence_speaking, 0) +
        func.coalesce(UserWordSkill.skill_sentence_listening, 0), 0
    )
    
    # 쿼리 실행
    stmt = (
        select(Word, level_priority.label('level_priority'), skill_sum.label('total_skill'))
        .options(
            selectinload(Word.examples),
            selectinload(Word.root_word).selectinload(Word.examples)
        )
        .outerjoin(UserWordSkill, (UserWordSkill.word_id == Word.id) & (UserWordSkill.user_id == user_id))
        .order_by(
            level_priority.asc(),  # level 우선순위 (낮은 숫자가 높은 우선순위)
            skill_sum.asc(),       # skill 총합이 작은 순
            func.random()          # 무작위 선택
        )
        .limit(limit)
    )
    
    result = db.execute(stmt).all()
    print(result, 'result')
    
    # Word 객체를 딕셔너리로 변환하여 반환 (순환 참조 방지)
    words_data = []
    for row in result:
        word = row[0]
        word_dict = {
            "id": word.id,
            "word": word.word,
            "jp_pronunciation": word.jp_pronunciation,
            "kr_pronunciation": word.kr_pronunciation,
            "kr_meaning": word.kr_meaning,
            "level": word.level,
            "user_id": word.user_id,
            "root_word_id": word.root_word_id,
            "examples": [
                {
                    "id": ex.id,
                    "jp_text": ex.jp_text,
                    "kr_text": ex.kr_text,
                    "jp_audio_url": ex.jp_audio_url,
                    "kr_audio_url": ex.kr_audio_url
                } for ex in word.examples
            ] if word.examples else []
        }
        
        # root_word의 예문도 추가
        if word.root_word and word.root_word.examples:
            root_examples = [
                {
                    "id": ex.id,
                    "jp_text": ex.jp_text,
                    "kr_text": ex.kr_text,
                    "jp_audio_url": ex.jp_audio_url,
                    "kr_audio_url": ex.kr_audio_url,
                    "is_root_example": True
                } for ex in word.root_word.examples
            ]
            word_dict["examples"].extend(root_examples)
        
        words_data.append(word_dict)
    
    return words_data 
    
