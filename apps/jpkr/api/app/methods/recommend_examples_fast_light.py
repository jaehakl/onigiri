from db import Example

from sqlalchemy import text, select
from sqlalchemy.orm import Session
from typing import List, Optional

def select_examples_fast_light(
    db: Session,
    user_id: str,
    *,
    words_k: int = 8,
    examples_per_word: int = 3,
    total_examples: Optional[int] = None,
    # 점수식
    tau0_days: float = 7.0,
    alpha: float = 1.5,
    lambda_R: float = 0.6,
    lambda_C: float = 0.25,
    lambda_D: float = 0.15,
    unseen_bonus: float = 0.3,
    gamma: float = 0.35,
    rand_eps: float = 0.02,
    exp_cap: float = 60.0,
    # === DB 부하 감소 파라미터 ===
    min_gap_days: int = 7,     # 이 기간 이상 안 본 단어만 1차 후보
    explore_p: float = 0.05,   # 프리필터와 무관하게 소량 탐험 포함
    sample_rows: int = 0,      # 매우 큰 words 테이블이면 TABLESAMPLE 사용
    overselect_factor: float = 1.5,
    randomize_in_app: bool = False,
) -> List[Example]:
    if total_examples is None:
        total_examples = words_k * examples_per_word

    tau0_sec = int(tau0_days * 24 * 3600)
    words_limit = int(max(1, words_k * overselect_factor))

    table_sample_clause = ""
    if sample_rows and sample_rows > 0:
        table_sample_clause = f" TABLESAMPLE SYSTEM_ROWS({int(sample_rows)}) "

    # DB에서 RANDOM()을 빼고 앱 셔플을 쓰려면 rand_term=0
    rand_term = "0" if randomize_in_app else ":rand_eps * RANDOM()"

    sql = f"""
    WITH skill AS (
      SELECT
        word_id,
        AVG((reading + listening + speaking) / 3.0) AS skill_val,
        MAX(updated_at) AS skill_updated_at
      FROM user_word_skills
      WHERE user_id = :user_id
      GROUP BY word_id
    ),
    -- 1) 프리필터: 처음 보거나, min_gap_days 이상 안 본 단어 + 소량 탐험
    base AS (
      SELECT
        w.id AS word_id,
        w.embedding AS w_emb,
        COALESCE(s.skill_val, 0.0) AS skill_val,
        COALESCE(s.skill_updated_at, '1970-01-01'::timestamptz) AS skill_updated_at,
        (s.skill_val IS NOT NULL) AS has_skill
      FROM words w {table_sample_clause}
      LEFT JOIN skill s ON s.word_id = w.id
      WHERE
            s.skill_val IS NULL
         OR (now() - COALESCE(s.skill_updated_at, '1970-01-01'::timestamptz))
              >= make_interval(days => :min_gap_days)
         OR (RANDOM() < :explore_p)
    ),
    -- 2) 프리필터된 단어에 한해 deg 집계
    deg AS (
      SELECT we.word_id, COUNT(*) AS deg
      FROM word_examples we
      WHERE we.word_id IN (SELECT word_id FROM base)
      GROUP BY we.word_id
    ),
    parts AS (
      SELECT
        b.word_id, b.w_emb, b.skill_val,
        COALESCE(d.deg, 0) AS deg,
        EXTRACT(EPOCH FROM (now() - b.skill_updated_at)) AS dt_sec,
        (:tau0_sec * (1 + :alpha * b.skill_val))::double precision AS tau_sec
      FROM base b
      LEFT JOIN deg d ON d.word_id = b.word_id
    ),
    scored AS (
      SELECT
        word_id, w_emb,
        -- R (underflow 방지)
        CASE
          WHEN tau_sec > 0
            THEN 1 - EXP(- LEAST(dt_sec / NULLIF(tau_sec, 0), :exp_cap))
          ELSE 1
        END AS R,
        -- C
        (0.7 / (1 + LN(1 + deg)) + CASE WHEN (skill_val > 0) THEN 0 ELSE :unseen_bonus END) AS C,
        -- D
        (1 - skill_val) AS D
      FROM parts
    ),
    rank_words AS (
      SELECT
        word_id, w_emb,
        (:lambda_R * R + :lambda_C * C + :lambda_D * D) {f"+ {rand_term}"} AS score
      FROM scored
    ),
    top_words AS (
      SELECT word_id, w_emb, score
      FROM rank_words
      ORDER BY score DESC
      LIMIT :words_limit
    ),
    picked AS (
      SELECT e.*
      FROM top_words tw
      JOIN LATERAL (
        SELECT e.*
        FROM word_examples we
        JOIN examples e ON e.id = we.example_id
        WHERE we.word_id = tw.word_id
          AND (
                tw.w_emb IS NULL OR e.embedding IS NULL
                OR (1 - (e.embedding <=> tw.w_emb)) >= :gamma
              )
        ORDER BY
          CASE
            WHEN tw.w_emb IS NULL OR e.embedding IS NULL
              THEN { '1' if randomize_in_app else 'RANDOM()' }
            ELSE (e.embedding <=> tw.w_emb) { '+ 0' if randomize_in_app else f'+ {rand_term}' }
          END ASC
        LIMIT :examples_per_word
      ) e ON TRUE
    )
    SELECT * FROM picked
    LIMIT :total_examples
    """

    params = {
        "user_id": user_id,
        "tau0_sec": tau0_sec,
        "alpha": alpha,
        "lambda_R": lambda_R,
        "lambda_C": lambda_C,
        "lambda_D": lambda_D,
        "unseen_bonus": unseen_bonus,
        "gamma": gamma,
        "rand_eps": rand_eps,
        "words_limit": words_limit,
        "examples_per_word": examples_per_word,
        "total_examples": total_examples,
        "exp_cap": exp_cap,
        "min_gap_days": int(min_gap_days),
        "explore_p": explore_p,
    }

    stmt = select(Example).from_statement(text(sql))
    result = db.execute(stmt, params).scalars().all()

    if randomize_in_app:
        from random import shuffle
        shuffle(result)

    return result[:total_examples]

