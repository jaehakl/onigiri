from typing import Optional

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from db import Example, WordExample
from utils.aws_s3 import presign_get_url


def filter_examples_by_criteria(
    min_words: Optional[int] = None,
    max_words: Optional[int] = None,
    has_en_prompt: Optional[bool] = None,
    has_embedding: Optional[bool] = None,
    has_audio: Optional[bool] = None,
    has_image: Optional[bool] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = None,
    user_id: Optional[str] = None,
):
    # 필요한 컬럼만 선택하여 쿼리 최적화(대용량 데이터 로드 방지)
    query = db.query(
        Example.id,
        Example.tags,
        Example.jp_text,
        Example.kr_mean,
        Example.en_prompt,
        Example.created_at,
        Example.updated_at,
        Example.image_object_key,
        # 존재 여부만 확인 (실제 값 로드하지 않음)
        case((Example.embedding.isnot(None), 1), else_=0).label("has_embedding"),
        case((Example.audio_object_key.isnot(None), 1), else_=0).label("has_audio"),
        case((Example.image_object_key.isnot(None), 1), else_=0).label("has_image"),
    )

    # 단어 수 필터링
    if min_words is not None or max_words is not None:
        example_count_subquery = (
            db.query(
                WordExample.example_id,
                func.count(WordExample.word_id).label("word_count"),
            )
            .group_by(WordExample.example_id)
            .subquery()
        )

        query = query.outerjoin(
            example_count_subquery, Example.id == example_count_subquery.c.example_id
        )

        if min_words is not None:
            query = query.filter(
                func.coalesce(example_count_subquery.c.word_count, 0) >= min_words
            )
        if max_words is not None:
            query = query.filter(
                func.coalesce(example_count_subquery.c.word_count, 0) <= max_words
            )

    if has_en_prompt is not None:
        query = query.filter(
            Example.en_prompt.isnot(None)
            if has_en_prompt
            else Example.en_prompt.is_(None)
        )

    # Embedding 보유 여부
    if has_embedding is not None:
        query = query.filter(
            Example.embedding.isnot(None)
            if has_embedding
            else Example.embedding.is_(None)
        )

    if has_audio is not None:
        query = query.filter(
            Example.audio_object_key.isnot(None)
            if has_audio
            else Example.audio_object_key.is_(None)
        )

    if has_image is not None:
        query = query.filter(
            Example.image_object_key.isnot(None)
            if has_image
            else Example.image_object_key.is_(None)
        )

    # 정렬 (ID 기준 내림차순)
    query = query.order_by(Example.id.desc())
    total_count = query.count()

    # 페이징
    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)

    rows = query.all()

    # 단어 개수 조회 (한 번만 실행)
    word_counts = {}
    if rows:
        example_ids = [row.id for row in rows]
        word_count_query = (
            db.query(
                WordExample.example_id,
                func.count(WordExample.word_id).label("word_count"),
            )
            .filter(WordExample.example_id.in_(example_ids))
            .group_by(WordExample.example_id)
        )
        word_counts = {row.example_id: row.word_count for row in word_count_query.all()}

    # 결과 구조화
    examples_rv = []
    for row in rows:
        examples_rv.append(
            {
                "id": row.id,
                "tags": row.tags,
                "jp_text": row.jp_text,
                "kr_mean": row.kr_mean,
                "en_prompt": row.en_prompt,
                "has_embedding": row.has_embedding,
                "has_audio": row.has_audio,
                "has_image": row.has_image,
                "image_url": presign_get_url(row.image_object_key, expires=600)
                if row.image_object_key is not None
                else None,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "num_words": word_counts.get(row.id, 0),
            }
        )

    return {"examples": examples_rv, "total_count": total_count}
