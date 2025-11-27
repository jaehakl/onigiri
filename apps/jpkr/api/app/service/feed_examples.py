from sqlalchemy.orm import Session
from typing import List

from db import Example
from methods.recommend_examples_worst_reading import recommend_examples_worst_reading
from methods.recommend_examples_simple import recommend_examples_simple
from methods.words_from_examples_batch import words_from_examples_batch

def get_examples_for_user(db: Session = None, tags: List[str] = None, user_id: str = None) -> List[Example]:
    if user_id is not None:
        examples = recommend_examples_worst_reading(limit_examples=12, tags=tags, db=db, user_id=user_id)
    else:
        examples = recommend_examples_simple(limit_examples=6, tags=tags, db=db)
    examples_result = list(words_from_examples_batch(examples, db=db, user_id=user_id).values())
    return examples_result