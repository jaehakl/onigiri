from typing import Dict, Any
from collections import defaultdict
from db import SessionLocal, Word, WordExample
from sqlalchemy.orm import selectinload
from sqlalchemy import select, case
from sqlalchemy.orm import Session
from utils.aws_s3 import presign_get_url

from service.analysis.words_from_text import extract_words_from_text

def row_to_dict(obj) -> dict:
    # ORM 객체를 dict로 안전하게 변환
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def analyze_text(text: str, db: Session=None, user_id:str = None) -> Dict[str, Any]:
    if db is None:
        db = SessionLocal()

    document, words_dict = extract_words_from_text(text)
        
    stmt = (
        select(Word)
        .options(selectinload(Word.word_examples)
                 .options(selectinload(WordExample.example)),
                 selectinload(Word.user_word_skills),)
        .where(Word.lemma_id.in_(list(words_dict.keys())))
        .order_by(
            case((Word.user_id == user_id, 0), else_=1)  # 내 것이 먼저 오게
        )
    )
    words = db.execute(stmt).scalars().all()

    # 그 다음엔 "처음 본 키만 채우기"만 해도 같은 효과
    words_existing = {}
    for w in words:
        if w.lemma_id and w.lemma_id not in words_existing:
            words_existing[w.lemma_id] = row_to_dict(w)
            words_existing[w.lemma_id]["examples"] = []
            words_existing[w.lemma_id]["user_word_skills"] = []
            words_existing[w.lemma_id]["user"] = row_to_dict(w.user)
            for user_word_skill in w.user_word_skills:
                words_existing[w.lemma_id]["user_word_skills"].append(row_to_dict(user_word_skill))
            for word_example in w.word_examples:
                example = word_example.example
                example_dict = {
                    "id": example.id,
                    "word_info": w.lemma,
                    "tags": example.tags,
                    "jp_text": example.jp_text,
                    "kr_mean": example.kr_mean,
                    "audio_url": presign_get_url(example.audio_object_key, expires=600) if example.audio_object_key else None,
                }
                words_existing[w.lemma_id]["examples"].append(example_dict)
                if len(words_existing[w.lemma_id]["examples"]) > 1:
                    break
    words_result = defaultdict(list)
    for i_line, line in enumerate(document):
        for i_word, word in enumerate(line):
            surface = word["surface"]
            lemma_id = word["lemma_id"]
            print(lemma_id)
            if lemma_id in words_existing:
                print(i_line, i_word, "found")
                w = words_existing[lemma_id]
                words_result[i_line].append({
                    "word_id": w["id"],
                    "lemma_id": w["lemma_id"],
                    "lemma": w["lemma"],
                    "user_id": w["user_id"],
                    "user_display_name": w["user"]["display_name"],
                    "surface": surface,
                    "jp_pron": w["jp_pron"],
                    "kr_pron": w["kr_pron"],
                    "kr_mean": w["kr_mean"],
                    "level": w["level"],
                    "examples": w["examples"],
                    "num_examples": len(w["examples"]),
                    "user_word_skills": w["user_word_skills"],
                    "num_user_word_skills": len(w["user_word_skills"]),
                })
            elif lemma_id in words_dict:
                if words_dict[lemma_id]["lemma"] != "":
                    print(i_line, i_word, "not found")
                    w = words_dict[lemma_id]
                    words_result[i_line].append({
                        "word_id": None,
                        "lemma_id": w["lemma_id"],
                        "lemma": w["lemma"],
                        "user_id": None,
                        "user_display_name": None,
                        "surface": surface,
                        "jp_pron": w["pronBase"],
                        "kr_pron": w["pos1"],
                        "kr_mean": w["type"],
                        "level": None,
                        "examples": [],
                        "num_examples": 0,
                        "user_word_skills": [],
                        "num_user_word_skills": 0,
                    })
    return words_result