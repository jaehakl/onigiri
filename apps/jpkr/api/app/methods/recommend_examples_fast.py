from sqlalchemy import text, select
from sqlalchemy.orm import Session
from typing import List, Optional
from db import Example

def select_examples_fast(
    db: Session,
    user_id: str,
    *,
    words_k: int = 8,
    examples_per_word: int = 3,
    total_examples: Optional[int] = None,
    # 점수식 파라미터
    tau0_days: float = 7.0,
    alpha: float = 1.5,
    lambda_R: float = 0.6,
    lambda_C: float = 0.25,
    lambda_D: float = 0.15,
    unseen_bonus: float = 0.3,
    # 임베딩ㆍ무작위
    gamma: float = 0.35,
    rand_eps: float = 0.03,
    # underflow 방지: exp(-x)에서 x 상한
    exp_cap: float = 60.0,   # 60이면 exp(-60) ≈ 8.8e-27 (사실상 0)
) -> List["Example"]:
    if total_examples is None:
        total_examples = words_k * examples_per_word

    tau0_sec = int(tau0_days * 24 * 3600)

    sql = """
    WITH skill AS (
      SELECT
        word_id,
        AVG((reading + listening + speaking) / 3.0) AS skill_val,
        MAX(updated_at) AS skill_updated_at
      FROM user_word_skills
      WHERE user_id = :user_id
      GROUP BY word_id
    ),
    deg AS (
      SELECT word_id, COUNT(*) AS deg
      FROM word_examples
      GROUP BY word_id
    ),
    base AS (
      SELECT
        w.id AS word_id,
        w.embedding AS w_emb,
        COALESCE(s.skill_val, 0.0) AS skill_val,
        COALESCE(s.skill_updated_at, '1970-01-01'::timestamptz) AS skill_updated_at,
        COALESCE(d.deg, 0) AS deg,
        EXTRACT(EPOCH FROM (now() - COALESCE(s.skill_updated_at, '1970-01-01'::timestamptz))) AS dt_sec,
        (s.skill_val IS NOT NULL) AS has_skill
      FROM words w
      LEFT JOIN skill s ON s.word_id = w.id
      LEFT JOIN deg   d ON d.word_id = w.id
    ),
    parts AS (
      SELECT
        word_id, w_emb, skill_val, deg, dt_sec,
        (:tau0_sec * (1 + :alpha * skill_val))::double precision AS tau_sec,
        CASE
          WHEN (:tau0_sec * (1 + :alpha * skill_val)) > 0
            THEN 1 - EXP(- LEAST( dt_sec / NULLIF((:tau0_sec * (1 + :alpha * skill_val)), 0), :exp_cap ))
          ELSE 1
        END AS R,
        (0.7 / (1 + LN(1 + deg)) + CASE WHEN has_skill THEN 0 ELSE :unseen_bonus END) AS C,
        (1 - skill_val) AS D
      FROM base
    ),
    scored AS (
      SELECT
        word_id, w_emb,
        :lambda_R * R + :lambda_C * C + :lambda_D * D
        + :rand_eps * RANDOM() AS score
      FROM parts
    ),
    top_words AS (
      SELECT word_id, w_emb, score,
             ROW_NUMBER() OVER (ORDER BY score DESC) AS rnk
      FROM scored
      ORDER BY score DESC
      LIMIT :words_limit
    ),
    picked AS (
      SELECT tw.rnk, e.*
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
              THEN RANDOM()
            ELSE (e.embedding <=> tw.w_emb) + :rand_eps * RANDOM()
          END ASC
        LIMIT :examples_per_word
      ) e ON TRUE
      ORDER BY tw.rnk, e.id
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
        "words_limit": words_k,
        "examples_per_word": examples_per_word,
        "total_examples": total_examples,
        "exp_cap": exp_cap,
    }

    stmt = select(Example).from_statement(text(sql))
    return db.execute(stmt, params).scalars().all()
