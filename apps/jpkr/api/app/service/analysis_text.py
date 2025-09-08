from typing import Dict, Any
from random import shuffle
from collections import defaultdict
from db import SessionLocal, Word, WordExample, UserWordSkill
from user_auth.db import User
from sqlalchemy.orm import selectinload
from sqlalchemy import select, case
from sqlalchemy.orm import Session
from utils.aws_s3 import presign_get_url

from utils.words_from_text import extract_words_from_text
from methods.words_from_examples_batch import words_from_examples_batch

def row_to_dict(obj) -> dict:
    # ORM 객체를 dict로 안전하게 변환
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def analyze_text(text: str, db: Session=None, user_id:str = None) -> Dict[str, Any]:
    if db is None:
        db = SessionLocal()

    document, words_dict = extract_words_from_text(text)
    
    # 필요한 필드만 선택하여 embedding 제외
    stmt = (
        select(
            Word.id,
            Word.user_id,
            Word.lemma_id,
            Word.lemma,
            Word.jp_pron,
            Word.kr_pron,
            Word.kr_mean,
            Word.level,
            User.display_name
        )
        .join(User, Word.user_id == User.id)
        .where(Word.lemma_id.in_(list(words_dict.keys())))
        .order_by(
            case((Word.user_id == user_id, 0), else_=1)  # 내 것이 먼저 오게
        )
    )
    word_rows = db.execute(stmt).all()
    
    # UserWordSkill은 별도 쿼리로 가져오기
    user_word_skills_stmt = (
        select(UserWordSkill)
        .where(UserWordSkill.word_id.in_([row.id for row in word_rows]))
    )
    user_word_skills = db.execute(user_word_skills_stmt).scalars().all()
    
    # word_id별로 user_word_skills 그룹화
    skills_by_word_id = defaultdict(list)
    for skill in user_word_skills:
        skills_by_word_id[skill.word_id].append(row_to_dict(skill))

    # words_existing 딕셔너리 구성
    words_existing = {}
    for row in word_rows:
        if row.lemma_id and row.lemma_id not in words_existing:
            words_existing[row.lemma_id] = {
                "id": row.id,
                "user_id": row.user_id,
                "lemma_id": row.lemma_id,
                "lemma": row.lemma,
                "jp_pron": row.jp_pron,
                "kr_pron": row.kr_pron,
                "kr_mean": row.kr_mean,
                "level": row.level,
                "user_word_skills": skills_by_word_id.get(row.id, []),
                "user": {"display_name": row.display_name}
            }

    words_result = defaultdict(list)
    for i_line, line in enumerate(document):
        for i_word, word in enumerate(line):
            surface = word["surface"]
            lemma_id = word["lemma_id"]
            if lemma_id in words_existing:
                w = words_existing[lemma_id]
                words_result[i_line].append({
                    "word_id": w["id"],
                    "lemma_id": w["lemma_id"],
                    "lemma": w["lemma"],
                    "user_id": w["user_id"],
                    "user_display_name": w["user"]["display_name"],
                    "surface": surface if w["lemma"] != "" else " "+surface,
                    "jp_pron": w["jp_pron"],
                    "kr_pron": w["kr_pron"],
                    "kr_mean": w["kr_mean"],
                    "level": w["level"],
                    "user_word_skills": w["user_word_skills"],
                    "num_user_word_skills": len(w["user_word_skills"]),
                })
            elif lemma_id in words_dict:
                if words_dict[lemma_id]["lemma"] != "":
                    w = words_dict[lemma_id]
                    words_result[i_line].append({
                        "word_id": None,
                        "lemma_id": w["lemma_id"],
                        "lemma": w["lemma"],
                        "user_id": None,
                        "user_display_name": None,
                        "surface": surface if w["lemma"] != "" else " "+surface,
                        "jp_pron": w["pronBase"],
                        "kr_pron": w["pos1"],
                        "kr_mean": w["type"],
                        "level": None,
                        "user_word_skills": [],
                        "num_user_word_skills": 0,
                    })
    return words_result