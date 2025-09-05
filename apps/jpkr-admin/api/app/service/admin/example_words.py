from typing import List, Dict, Any
from sqlalchemy.orm import Session

from service.analysis.words_from_text import extract_words_from_text
from db import Example, WordExample, Word


def gen_example_words(
    example_ids: List[int],
    db: Session,
    user_id: str
) -> Dict[str, Any]:
    examples = db.query(Example).filter(Example.id.in_(example_ids)).all()

    words_dict_global = {}

    for i, example in enumerate(examples):
        document, words_dict = extract_words_from_text(example.jp_text)
        words_dict_global.update(words_dict)

    words_existing = db.query(Word).filter(Word.lemma_id.in_(list(words_dict_global.keys()))
                                            ).where(Word.user_id == user_id).all()
    words_dict_existing = {w.lemma_id: w.id for w in words_existing}
    for lemma_id, word_data in words_dict_global.items():
        if lemma_id not in words_dict_existing:
            pos = word_data["pos1"]
            level = "N1"
            if pos in ["助詞", "記号", "助動詞","補助記号","接尾辞", "代名詞"]:
                continue
            new_word = Word(
                user_id=user_id,
                lemma_id=lemma_id,
                lemma=word_data["lemma"],
                jp_pron=word_data["pronBase"],
                kr_pron=word_data["pos1"],
                kr_mean=word_data["type"],
                level=level,
            )
            db.add(new_word)
            db.flush()
            words_dict_existing[lemma_id] = new_word.id
        else:
            pass
    for i, example in enumerate(examples):
        document, words_dict = extract_words_from_text(example.jp_text)
        for word_data in words_dict.values():
            if word_data["lemma_id"] not in words_dict_existing:
                continue
            new_word_example = WordExample(
                word_id=words_dict_existing[word_data["lemma_id"]],
                example_id=example.id
            )
            db.add(new_word_example)
            db.flush()
    db.commit()
    return {"message": "Example words generated successfully"}