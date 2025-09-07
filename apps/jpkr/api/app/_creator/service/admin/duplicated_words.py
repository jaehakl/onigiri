from typing import Dict, List, Optional, Set
from sqlalchemy import select, and_, func, exists
from sqlalchemy.orm import Session, selectinload, aliased
from collections import defaultdict

from db import Word  # SQLAlchemy ORM model

def get_duplicated_words(db: Session, user_id: Optional[str] = None) -> Dict[str, List[dict]]:
    # 1. 중복된 컬럼 값만 추출하는 서브쿼리
    dup_values_subq = (
        select(Word.lemma_id)
        .group_by(Word.lemma_id)
        .having(func.count() >= 2)
        .subquery()
    )

    # 2. 원본 테이블과 join 해서 해당 row 들 선택
    stmt = (
        select(Word)
        .join(dup_values_subq, Word.lemma_id == dup_values_subq.c.lemma_id)
    )
    rows = db.execute(stmt).scalars().all()


    def row_to_dict(r) -> dict:
        # r는 Word 객체이므로 속성에 직접 접근
        return {
            'id': r.id,
            'lemma_id': r.lemma_id,
            'lemma': r.lemma,
            'jp_pron': r.jp_pron,
            'kr_pron': r.kr_pron,
            'kr_mean': r.kr_mean,
            'level': r.level,
            'num_examples': len(r.word_examples),
            'has_embedding': 1 if r.embedding is not None else 0,
            'user_id': r.user.id if r.user else None,
            'user_name': r.user.display_name if r.user else None,
            'created_at': r.created_at.isoformat() if r.created_at else None,
            'updated_at': r.updated_at.isoformat() if r.updated_at else None,
        }
    
    groups: Dict[str, List[dict]] = defaultdict(list)
    for r in rows:
        groups[r.lemma_id].append(row_to_dict(r))

    return groups