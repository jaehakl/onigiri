from typing import List, Optional

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from db import Word, WordExample


def filter_words_by_criteria(
    levels: Optional[List[str]] = None,
    min_examples: Optional[int] = None,
    max_examples: Optional[int] = None,
    has_embedding: Optional[bool] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = None,
    user_id: Optional[str] = None,
):
    """
    Words 테이블에서 다양한 기준으로 필터링한 목록을 반환한다.
    """
    # 필요한 컬럼만 선택 (embedding 값 자체는 로드하지 않음)
    query = db.query(
        Word.id,
        Word.lemma_id,
        Word.lemma,
        Word.jp_pron,
        Word.kr_pron,
        Word.kr_mean,
        Word.level,
        Word.created_at,
        case((Word.embedding.isnot(None), 1), else_=0).label("has_embedding"),
    )

    # 레벨 필터
    if levels:
        query = query.filter(Word.level.in_(levels))

    # 예문 개수 필터
    if min_examples is not None or max_examples is not None:
        example_count_subquery = (
            db.query(
                WordExample.word_id,
                func.count(WordExample.example_id).label("example_count"),
            )
            .group_by(WordExample.word_id)
            .subquery()
        )

        query = query.outerjoin(
            example_count_subquery, Word.id == example_count_subquery.c.word_id
        )

        if min_examples is not None:
            query = query.filter(
                func.coalesce(example_count_subquery.c.example_count, 0)
                >= min_examples
            )
        if max_examples is not None:
            query = query.filter(
                func.coalesce(example_count_subquery.c.example_count, 0)
                <= max_examples
            )

    # Embedding 보유 여부 필터
    if has_embedding is not None:
        query = query.filter(
            Word.embedding.isnot(None)
            if has_embedding
            else Word.embedding.is_(None)
        )

    # 정렬 (생성일 기준 내림차순)
    query = query.order_by(Word.created_at.desc())
    total_count = query.count()

    # 페이징
    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)

    rows = query.all()

    # 예문 개수 조회 (한 번만 실행)
    example_counts = {}
    if rows:
        word_ids = [row.id for row in rows]
        example_count_query = (
            db.query(
                WordExample.word_id,
                func.count(WordExample.example_id).label("example_count"),
            )
            .filter(WordExample.word_id.in_(word_ids))
            .group_by(WordExample.word_id)
        )
        example_counts = {
            row.word_id: row.example_count for row in example_count_query.all()
        }

    words_rv = []
    for row in rows:
        words_rv.append(
            {
                "id": row.id,
                "lemma_id": row.lemma_id,
                "lemma": row.lemma,
                "jp_pron": row.jp_pron,
                "kr_pron": row.kr_pron,
                "kr_mean": row.kr_mean,
                "level": row.level,
                "num_examples": example_counts.get(row.id, 0),
                "has_embedding": row.has_embedding,
            }
        )

    return {"words": words_rv, "total_count": total_count}
