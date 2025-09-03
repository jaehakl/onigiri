from typing import List, Dict, Any

from fugashi import Tagger
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import text, select, or_, case

from db import Example, WordExample, Word

def row_to_dict(obj) -> dict:
    # ORM 객체를 dict로 안전하게 변환
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def gen_example_words(
    example_ids: List[str],
    db: Session,
    user_id: str
) -> Dict[str, Any]:
    examples = db.query(Example).filter(Example.id.in_(example_ids)).all()

    tagger = Tagger()  # unidic-lite 자동 사용    
    rows = []
    word_list = []

    for i, example in enumerate(examples):
        text_words = tagger(example.jp_text)
        for i_word, word in enumerate(text_words):
            feat = word.feature
            pos  = getattr(feat, "pos1", "")
            rows.append({
                "example_id": example.id,
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

    lemmas = [r["lemma"] for r in rows]
    stmt = (
        select(Word)
        .options(selectinload(Word.word_examples))
        .where(
            or_(
                Word.word.in_(lemmas) if lemmas else False,
            )
        )
        .order_by(
            case((Word.user_id == user_id, 0), else_=1)  # 내 것이 먼저 오게
        )
    )
    words = db.execute(stmt).scalars().all()
    # 그 다음엔 "처음 본 키만 채우기"만 해도 같은 효과
    by_lemma = {}
    for w in words:
        if w.word and w.word not in by_lemma:
            by_lemma[w.word] = [w.id, [we.example_id for we in w.word_examples]]
    
    for row in rows:
        if row["lemma"] == None:
            continue
        w = by_lemma.get(row["lemma"])
        if w:
            w_id = w[0]
            w_example_ids = w[1]
        else:
            word = Word(
                word=row["lemma"],
                jp_pronunciation=row["reading"],
                kr_pronunciation=row["pos"],
                kr_meaning=row["pos2"],
                level="N1",
                user_id=user_id,
            )
            db.add(word)
            db.flush()
            if row["lemma"] not in by_lemma:
                by_lemma[row["lemma"]] = [word.id, []]
            w_id = word.id
            w_example_ids = []
        if row["example_id"] not in w_example_ids:
            word_example = WordExample(
                word_id=w_id,
                example_id=row["example_id"],
            )
            db.add(word_example)
            db.flush()
            by_lemma[row["lemma"]][1].append(row["example_id"])
    db.commit()
    return {"message": "Example words generated successfully"}