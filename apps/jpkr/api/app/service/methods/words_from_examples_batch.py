from sqlalchemy.orm import Session, selectinload
from typing import List, Dict, Any
from collections import defaultdict

from db import Example, Word
from utils.aws_s3 import presign_get_url
from service.analysis.words_from_text import extract_words_from_text

def row_to_dict(obj) -> dict:
    # ORM 객체를 dict로 안전하게 변환
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def words_from_examples_batch(examples: List[Example], db: Session = None, user_id: str = None) -> Dict[int, Dict[str, Any]]:
    words_dict_global = {}
    for i, example in enumerate(examples):
        document, words_dict = extract_words_from_text(example.jp_text)
        words_dict_global.update(words_dict)

    words_existing = (db.query(Word)
                    .options(selectinload(Word.user_word_skills),
                            selectinload(Word.user)
                        )
                    .filter(Word.lemma_id.in_(list(words_dict_global.keys()))
                                                            ).where(Word.user_id == user_id).all())
    words_dict_existing = {}

    for w in words_existing:
        if w.lemma_id and w.lemma_id not in words_dict_existing:
            words_dict_existing[w.lemma_id] = row_to_dict(w)
            words_dict_existing[w.lemma_id]["user_word_skills"] = []
            words_dict_existing[w.lemma_id]["user"] = row_to_dict(w.user)
            for user_word_skill in w.user_word_skills:
                words_dict_existing[w.lemma_id]["user_word_skills"].append(row_to_dict(user_word_skill))


    examples_result = {}
    for example in examples:
        document, words_dict = extract_words_from_text(example.jp_text)
        example.words_dict = words_dict

        words_result = defaultdict(list)
        for i_line, line in enumerate(document):
            for i_word, word in enumerate(line):
                surface = word["surface"]
                lemma_id = word["lemma_id"]
                if lemma_id in words_dict_existing:
                    w = words_dict_existing[lemma_id]
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
                        "user_word_skills": w["user_word_skills"],
                        "num_user_word_skills": len(w["user_word_skills"]),
                    })
                elif lemma_id in words_dict_global:
                    if words_dict_global[lemma_id]["lemma"] != "":
                        w = words_dict_global[lemma_id]
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
                            "user_word_skills": [],
                            "num_user_word_skills": 0,
                        })
        examples_result[example.id] = {
            "id": example.id,
            "jp_text": example.jp_text,
            "kr_mean": example.kr_mean,
            "tags": example.tags,
            "audio_url": presign_get_url(example.audio_object_key, expires=600) if example.audio_object_key is not None else None,
            "image_url": presign_get_url(example.image_object_key, expires=600) if example.image_object_key is not None else None,
            "words": words_result,
        }
    return examples_result