from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, select

from db import Word
from service.analysis.embedding import get_text_embedding

def gen_word_embeddings(
    word_ids: List[str],
    db: Session,
    user_id: str
) -> Dict[str, Any]:
    words = db.query(Word).filter(Word.id.in_(word_ids)).all()
    for i, word in enumerate(words):
        word.embedding = get_text_embedding(word.word)
        if i % 10 == 0:
            print(f"Generated embedding for word {i+1}/{len(words)}")
    db.commit()
    return {"message": "Embeddings generated successfully"}