from datetime import datetime, timezone
from sqlalchemy import func, select, and_
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from db import Example, WordExample, Word, UserWordSkill

def recommend_examples_simple(limit_examples: int = 30, db: Session = None, user_id: str = None) -> List[Example]:
    stmt_ex = select(Example).order_by(func.random()).limit(max(1, limit_examples))
    examples = db.execute(stmt_ex).scalars().all()
    return examples