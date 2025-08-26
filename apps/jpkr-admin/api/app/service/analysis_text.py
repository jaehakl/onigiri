import re
from typing import List, Dict, Any
from fugashi import Tagger
from collections import defaultdict
from db import SessionLocal, Word, Example
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

def analyze_text(text: str, db: Session=None, user_id:str = None) -> Dict[str, Any]:
    if db is None:
        db = SessionLocal()

    tagger = Tagger()  # unidic-lite 자동 사용    
    rows = []
    word_list = []    
    text_list = text.split("\n")
    for i_line, text in enumerate(text_list):
        text_words = tagger(text)
        for i_word, word in enumerate(text_words):
            feat = word.feature
            pos  = getattr(feat, "pos1", "")
            #if pos in ["助詞", "記号", "助動詞","補助記号","接尾辞"]:
            #    continue
            #if word.surface.strip() in word_list:
            #    continue
            rows.append({
                "i_line": i_line,
                "i_word": i_word,
                "surface": word.surface if getattr(feat, "lemma", None) != None else " "+word.surface,
                "lemma": getattr(feat, "lemma", None),
                "pos": pos,
                "pos2": getattr(feat, "pos2", ""),
                "pos3": getattr(feat, "pos3", ""),
                "pos4": getattr(feat, "pos4", ""),
                "cType": getattr(feat, "cType", ""),
                "cForm": getattr(feat, "cForm", ""),
                "reading": getattr(feat, "reading", ""),
            })
            word_list.append(word.surface)
        

    # rows 에서 필요한 키들 수집 (중복 제거)
    lemmas = [r["lemma"] for r in rows]
    surfaces = [r["surface"] for r in rows]
    stmt = (
        select(Word)
        .options(selectinload(Word.examples), selectinload(Word.user_word_skills))
        .where(
            or_(
                Word.word.in_(lemmas) if lemmas else False,
                Word.jp_pronunciation.in_(surfaces) if surfaces else False,
            )
        )
    )
    words = db.execute(stmt).scalars().all()
    # 이후는 words 를 바탕으로 같은 방식으로 매칭

    # 2) 빠른 조회를 위한 맵 구성
    by_lemma = {}
    by_surface = {}
    for w in words:
        if w.word and w.word not in by_lemma:
            by_lemma[w.word] = w
        if w.jp_pronunciation and w.jp_pronunciation not in by_surface:
            by_surface[w.jp_pronunciation] = w

    # 4) 원래 rows 순서를 유지하며 결과 구성 (lemma 우선, 없으면 surface)
    words_result = defaultdict(list)
    for r in rows:
        w = by_lemma.get(r.get("lemma"))
        if not w:
            if len(r.get("surface")) > 2:
                w = by_surface.get(r.get("surface"))
        if w:
            examples_list = []
            for example in w.examples:
                examples_list.append({
                    "id": example.id,
                    "word_info": example.word.word,
                    "tags": example.tags,
                    "jp_text": example.jp_text,
                    "kr_meaning": example.kr_meaning,
                })
            user_word_skills_list = []
            for user_word_skill in w.user_word_skills:
                user_word_skills_list.append({
                    "id": user_word_skill.id,
                    "skill_kanji": user_word_skill.skill_kanji,
                    "skill_word_reading": user_word_skill.skill_word_reading,
                    "skill_word_speaking": user_word_skill.skill_word_speaking,
                    "skill_sentence_reading": user_word_skill.skill_sentence_reading,
                    "skill_sentence_speaking": user_word_skill.skill_sentence_speaking,
                    "skill_sentence_listening": user_word_skill.skill_sentence_listening,
                    "is_favorite": user_word_skill.is_favorite,
                })
            user_word_skills_list = sorted(user_word_skills_list, key=lambda x: x["skill_kanji"], reverse=True)
            words_result[r["i_line"]].append({
                "word_id": w.id,
                "word": w.word,
                "surface": r["surface"],
                "jp_pronunciation": w.jp_pronunciation,
                "kr_pronunciation": w.kr_pronunciation,
                "kr_meaning": w.kr_meaning,
                "level": w.level,
                "examples": examples_list,
                "num_examples": len(examples_list),
                "user_word_skills": user_word_skills_list,
                "num_user_word_skills": len(user_word_skills_list),
            })
        elif r["lemma"] != "":
            words_result[r["i_line"]].append({
                "word_id": None,
                "word": r["lemma"],
                "surface": r["surface"],
                "jp_pronunciation": "",
                "kr_pronunciation": "",
                "kr_meaning": "",
                "level": "N/A",
                "examples": [],
                "num_examples": 0,
                "user_word_skills": [],
                "num_user_word_skills": 0,
            })
    return words_result