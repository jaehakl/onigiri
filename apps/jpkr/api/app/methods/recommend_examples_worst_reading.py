import random
from typing import List, Optional

from sqlalchemy import func, select, or_
from sqlalchemy.orm import Session

from db import Example, WordExample, Word, UserWordSkill
from models import ExampleOut
from utils.aws_s3 import presign_get_url


def recommend_examples_worst_reading(
    limit_examples: int = 30,
    tags: Optional[List[str]] = None,
    db: Session = None,
    user_id: str = None
) -> List[ExampleOut]:
    """
    Pick examples by prioritizing words with the lowest reading scores.
    Steps:
    1) Gather user reading scores per word (missing -> 100 to deprioritize).
    2) Optionally restrict to words that have examples matching provided tags.
    3) Weighted random pick of words (weight inversely proportional to reading).
    4) For each chosen word, pick a random example linked via WordExample (tag-filtered if provided).
    5) Deduplicate examples and return up to limit_examples.
    """
    if user_id is None:
        return []

    # Precompute OR filter for tags, reused below
    tag_filters = None
    if tags:
        tag_filters = [Example.tags.ilike(f"%{tag}%") for tag in tags if tag]

    # 1) Load reading scores per word for this user
    word_scores = db.execute(
        select(
            Word.id.label("word_id"),
            func.coalesce(UserWordSkill.reading, 100).label("reading_score"),
        )
        .select_from(Word)
        .outerjoin(
            UserWordSkill,
            (UserWordSkill.word_id == Word.id) & (UserWordSkill.user_id == user_id),
        )
    ).all()

    if not word_scores:
        return []

    # 2) If tag filters exist, keep only words that have at least one matching example
    if tag_filters:
        candidate_word_ids = db.execute(
            select(WordExample.word_id)
            .select_from(WordExample)
            .join(Example, Example.id == WordExample.example_id)
            .where(or_(*tag_filters))
            .distinct()
        ).scalars().all()
        candidate_word_ids_set = set(candidate_word_ids)
        word_scores = [ws for ws in word_scores if ws.word_id in candidate_word_ids_set]
        if not word_scores:
            return []

    # 2) Build weights (lower reading -> higher weight)
    weights = []
    words = []
    for row in word_scores:
        score = row.reading_score or 0
        #weight = max(1, 101 - min(100, score))  # score 0 -> 101, score 100 -> 1
        weight = 2525 - (50 - min(100, score)) ** 2
        weights.append(weight)
        words.append(row.word_id)

    chosen_examples = []
    seen_example_ids = set()

    # 3) Sample words with replacement using weights, then pick random example per word
    sample_size = min(limit_examples * 4, len(words))  # buffer to offset duplicates
    for word_id in random.choices(words, weights=weights, k=sample_size):
        stmt = (
            select(
                Example.id,
                Example.jp_text,
                Example.kr_mean,
                Example.en_prompt,
                Example.audio_object_key,
                Example.image_object_key,
                Example.tags,
            )
            .select_from(Example)
            .join(WordExample, WordExample.example_id == Example.id)
            .where(WordExample.word_id == word_id)
        )

        if tag_filters:
            stmt = stmt.where(or_(*tag_filters))

        example_row = db.execute(
            stmt.order_by(func.random()).limit(1)
        ).first()

        if example_row and example_row.id not in seen_example_ids:
            seen_example_ids.add(example_row.id)
            chosen_examples.append(
                ExampleOut(
                    id=example_row.id,
                    jp_text=example_row.jp_text,
                    kr_mean=example_row.kr_mean,
                    en_prompt=example_row.en_prompt,
                    audio_url=presign_get_url(example_row.audio_object_key, expires=600)
                    if example_row.audio_object_key
                    else None,
                    image_url=presign_get_url(example_row.image_object_key, expires=600)
                    if example_row.image_object_key
                    else None,
                    tags=example_row.tags,
                )
            )

        if len(chosen_examples) >= limit_examples:
            break

    return chosen_examples
