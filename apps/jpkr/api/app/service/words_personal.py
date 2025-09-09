from typing import List, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, case
from db import Word, UserWordSkill

import json
from fastapi import UploadFile, File, Form, HTTPException
from utils.aws_s3 import presign_get_url

async def create_words_personal(
    data_json: str = Form(...),                     # 단어 배열(JSON string)
    file_meta_json: str = Form("[]"),               # 파일 메타(JSON string; files 인덱스와 매칭)
    files: List[UploadFile] = File(default=[]),     # 이미지 파일들
    db: Session=None,
    user_id:str=None
):
    try:
        data: List[Dict[str, Any]] = json.loads(data_json)
    except Exception:
        raise HTTPException(400, detail="data_json must be a JSON array")

    try:
        file_meta: List[Dict[str, Any]] = json.loads(file_meta_json)
    except Exception:
        raise HTTPException(400, detail="file_meta_json must be a JSON array")

    if len(file_meta) != len(files):
        raise HTTPException(400, detail="file_meta_json length must match files length")

    # ---------- 1) 단어 upsert ----------
    created_words: List[str] = []
    updated_words: List[str] = []
    created_skills: List[str] = []
    updated_skills: List[str] = []

    # word → payload 매핑
    words_map = {}
    for wrec in data:
        if wrec["lemma_id"] is None or wrec["lemma_id"] == "":
            continue
        else:
            try:
                lemma_id = int(wrec["lemma_id"])
                words_map[lemma_id] = wrec
            except:
                continue
    # 기존 단어 로드
    stmt = (
        select(Word)
        .options(selectinload(Word.word_examples), selectinload(Word.user_word_skills))
        .where(Word.lemma_id.in_(list(words_map.keys())))
    )
    words_existing = db.execute(stmt).scalars().all()
    words_existing_map = {w.lemma_id: w for w in words_existing}

    # upsert 처리
    word_id_map: Dict[str, str] = {}  # word 텍스트 -> 실제 Word.id
    for word, payload in words_map.items():
        new_word_id = None
        if word not in words_existing_map or str(words_existing_map[word].user_id )!= user_id:
            new_word = Word(
                user_id=user_id,
                lemma_id=payload.get('lemma_id'),
                lemma=payload.get('lemma'),
                jp_pron=payload.get('jp_pron'),
                kr_pron=payload.get('kr_pron'),
                kr_mean=payload.get('kr_mean'),
                level=payload.get('level'),
            )
            db.add(new_word)
            db.flush()
            created_words.append(word)
            new_word_id = new_word.id
            words_existing_map[word] = new_word
        else:
            # 본인 소유 → 업데이트
            row = words_existing_map[word]
            row.lemma_id = payload.get('lemma_id')
            row.lemma = payload.get('lemma')
            row.jp_pron = payload.get('jp_pron')
            row.kr_pron = payload.get('kr_pron')
            row.kr_mean = payload.get('kr_mean')
            row.level = payload.get('level')
            updated_words.append(row.lemma_id)
            new_word_id = row.id

        word_id_map[word] = new_word_id
        # skill 자동처리 (예: level == 'N/A' → 읽기 100)
        if payload.get('reading_mastered') == True:
            existing_skill = db.query(UserWordSkill).filter(
                UserWordSkill.user_id == user_id,
                UserWordSkill.word_id == new_word_id
            ).first()
            if existing_skill:
                setattr(existing_skill, 'reading', 100)
                updated_skills.append(word)
            else:
                new_skill = UserWordSkill(
                    user_id=user_id,
                    word_id=new_word_id,
                    reading=100,
                    listening=0,
                    speaking=0,
                )
                db.add(new_skill)
                db.flush()
                created_skills.append(word)
        else:
            existing_skill = db.query(UserWordSkill).filter(
                UserWordSkill.user_id == user_id,
                UserWordSkill.word_id == new_word_id
            ).first()
            if existing_skill:
                if existing_skill.reading < 80:
                    existing_skill.reading += 1
                    updated_skills.append(word)
                else:
                    existing_skill.reading = 0
                    updated_skills.append(word)
            else:
                new_skill = UserWordSkill(
                    user_id=user_id,
                    word_id=new_word_id,
                    reading=1,
                    listening=0,
                    speaking=0,
                )
                db.add(new_skill)
                db.flush()
                created_skills.append(word)


    db.commit()

    return {
        "success": True,
        "created_words": created_words,
        "updated_words": updated_words,
        "created_skills": created_skills,
        "updated_skills": updated_skills,
    }

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
        func.coalesce(UserWordSkill.reading, 0) +
        func.coalesce(UserWordSkill.listening, 0) +
        func.coalesce(UserWordSkill.speaking, 0), 0
    )
    
    # 쿼리 실행
    stmt = (
        select(Word, level_priority.label('level_priority'), skill_sum.label('total_skill'))
        .options(
            selectinload(Word.word_examples),
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
    
    # Word 객체를 딕셔너리로 변환하여 반환 (순환 참조 방지)
    words_data = []
    for row in result:
        word = row[0]
        word_dict = {
            "id": word.id,
            "lemma_id": word.lemma_id,
            "lemma": word.lemma,
            "jp_pron": word.jp_pron,
            "kr_pron": word.kr_pron,
            "kr_mean": word.kr_mean,
            "level": word.level,
            "user_id": word.user_id,
            "examples": [
                {
                    "id": wex.example.id,
                    "word_info": word.lemma,
                    "tags": wex.example.tags,
                    "jp_text": wex.example.jp_text,
                    "kr_mean": wex.example.kr_mean,
                    "audio_url": presign_get_url(wex.example.audio_object_key, expires=600) if wex.example.audio_object_key else None,
                } for wex in word.word_examples
            ] if word.word_examples else []
        }
        words_data.append(word_dict)    
    return words_data 
    
