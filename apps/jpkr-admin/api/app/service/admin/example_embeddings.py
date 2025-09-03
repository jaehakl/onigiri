from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, select

from db import Example
from service.analysis.embedding import get_text_embedding

def gen_example_embeddings(
    example_ids: List[str],
    db: Session,
    user_id: str
) -> Dict[str, Any]:
    examples = db.query(Example).filter(Example.id.in_(example_ids)).all()
    for i, example in enumerate(examples):
        example.embedding = get_text_embedding(example.jp_text)
        if i % 10 == 0:
            print(f"Generated embedding for example {i+1}/{len(examples)}")
    db.commit()
    return {"message": "Embeddings generated successfully"}