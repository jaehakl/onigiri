import re
from typing import List, Dict, Any
from fugashi import Tagger
from db import SessionLocal, Words, Examples


def analyze_text(text: str) -> Dict[str, Any]:
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
            if getattr(feat, "lemma", None) != None:
                rows.append({
                    "i_line": i_line,
                    "i_word": i_word,
                    "surface": word.surface,    
                    "lemma": getattr(feat, "lemma", None).split("-")[0].strip(),
                    "pos": pos,
                    "pos2": getattr(feat, "pos2", ""),
                    "pos3": getattr(feat, "pos3", ""),
                    "pos4": getattr(feat, "pos4", ""),
                    "cType": getattr(feat, "cType", ""),
                    "cForm": getattr(feat, "cForm", ""),
                    "reading": getattr(feat, "reading", ""),
                })
                word_list.append(word.surface)


    words_result = {}
    db = SessionLocal()
    for row in rows:
        if row["i_line"] not in words_result:
            words_result[row["i_line"]] = []

        word = db.query(Words).filter(Words.word == row["lemma"]).first()
        if not word:
            word = db.query(Words).filter(Words.jp_pronunciation == row["surface"]).first()
        if word:            
            examples = db.query(Examples).filter(Examples.word_id == word.id).all()
            examples_list = []
            for example in examples:
                examples_list.append({
                    "id": example.id,
                    "word_info": example.word.word,
                    "tags": example.tags,
                    "jp_text": example.jp_text,
                    "kr_meaning": example.kr_meaning,
                    "updated_at": example.updated_at
                })
            words_result[row["i_line"]].append({
                "word_id": word.id,
                "word": word.word,
                "surface": row["surface"],
                "jp_pronunciation": word.jp_pronunciation,
                "kr_pronunciation": word.kr_pronunciation,
                "kr_meaning": word.kr_meaning,
                "level": word.level,
                "examples": examples_list,
                "num_examples": len(examples_list),
                "updated_at": word.updated_at
            })
        elif row["lemma"] != "":
            words_result[row["i_line"]].append({
                "word_id": None,
                "word": row["lemma"],
                "surface": row["surface"],
                "jp_pronunciation": "",
                "kr_pronunciation": "",
                "kr_meaning": "",
                "level": "N/A",
                "updated_at": ""
            })
    return words_result