from sqlalchemy.orm import Session
from typing import List

from db import Example
from service.methods.recommend_examples_fast import select_examples_fast
from service.methods.recommend_examples_fast_light import select_examples_fast_light
from service.methods.recommend_examples import recommend_examples
from service.methods.recommend_examples_advanced import select_examples_for_user_randomized
from service.methods.words_from_examples_batch import words_from_examples_batch

def get_examples_for_user(db: Session = None, user_id: str = None) -> List[Example]:
    #examples = recommend_examples(db=db, user_id=user_id)
    #examples = select_examples_for_user_randomized(words_k=30, examples_per_word=3, db=db, user_id=user_id)
    examples = select_examples_fast(words_k=30, examples_per_word=3, db=db, user_id=user_id)
    #examples = select_examples_fast_light(words_k=30, examples_per_word=3, db=db, user_id=user_id)
    examples_result = list(words_from_examples_batch(examples, db=db, user_id=user_id).values())
    return examples_result