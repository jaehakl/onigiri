from __future__ import annotations

from typing import List
from sqlalchemy import (create_engine, MetaData, func,
    text, Text,DateTime,Integer,ForeignKey,Index,)
from sqlalchemy.orm import (DeclarativeBase,mapped_column,Mapped,relationship,sessionmaker,)
from sqlalchemy.dialects.postgresql import (UUID)
from pgvector.sqlalchemy import Vector

import fugashi
import unidic
from to_tsv import to_hangul

from db import Word, SessionLocal, User

if __name__ == "__main__":
    print("start")

    existing_words = {}
    # 세션으로 쿼리 실행
    with SessionLocal() as session:
        user = session.query(User).first()
        words = session.query(Word).all()
        for w in words:
            existing_words[w.lemma_id] = w


    new_words = {}
    with open("JLPTwords.txt", "r", encoding="utf-8") as file:
        tagger = fugashi.Tagger('-d "{}"'.format(unidic.DICDIR))

        for line in file:
            japanese = line.split(",")[0].split("N")[0]
            kana =japanese.split("[")[0]
            writing = kana
            if len(japanese.split("[")) > 1:
                writing = japanese.split("[")[1].split("]")[0]
            hangul = to_hangul(kana.strip())
            korean = line.split(",")[1].strip("\n")
            grade = "N"+line.split(",")[0].split("N")[1]


            word = tagger(writing)[0]
            feat = word.feature
            lemma_id = int(getattr(feat, "lemma_id", None)) if getattr(feat, "lemma_id", None) else None
            lemma = getattr(feat, "lemma", None)
            pronBase = getattr(feat, "pronBase", None)
            if lemma_id is None:
                continue
            new_words[lemma_id] = {
                "lemma_id": lemma_id,
                "lemma": lemma,
                "jp_pron": pronBase,
                "kr_pron": hangul,
                "kr_mean": korean,
                "level": grade
            }

    new_count = len(new_words)
    existing_count = len(existing_words)
    overlap_count = 0

    for lemma_id, word_data in new_words.items():
        if lemma_id in existing_words:
            existing_words[lemma_id].user_id = user.id
            existing_words[lemma_id].lemma = word_data["lemma"]
            existing_words[lemma_id].jp_pron = word_data["jp_pron"]
            existing_words[lemma_id].kr_pron = word_data["kr_pron"]
            existing_words[lemma_id].kr_mean = word_data["kr_mean"]
            existing_words[lemma_id].level = word_data["level"]
            overlap_count += 1
        else:
            new_word = Word(
                user_id=user.id,
                lemma_id=lemma_id,
                lemma=word_data["lemma"],
                jp_pron=word_data["jp_pron"],
                kr_pron=word_data["kr_pron"],
                kr_mean=word_data["kr_mean"],
                level=word_data["level"]
            )
            session.add(new_word)
    try:
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()

    print(f"new_count: {new_count}, existing_count: {existing_count}, overlap_count: {overlap_count}")
