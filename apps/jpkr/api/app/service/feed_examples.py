from sqlalchemy.orm import Session
from typing import List

from db import Example
from methods.recommend_examples_simple import recommend_examples_simple
from methods.words_from_examples_batch import words_from_examples_batch

def get_examples_for_user(db: Session = None, user_id: str = None) -> List[Example]:
    examples = recommend_examples_simple(limit_examples=6, db=db, user_id=user_id)
    examples_result = list(words_from_examples_batch(examples, db=db, user_id=user_id).values())
    return examples_result