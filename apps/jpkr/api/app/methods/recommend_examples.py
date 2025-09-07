import math
from datetime import datetime, timezone
from sqlalchemy import func, select, and_
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from db import Example, WordExample, Word, UserWordSkill

def recommend_examples(limit_words: int = 30, limit_examples: int = 30, db: Session = None, user_id: str = None) -> List[Example]:
    """
    - UserWordSkill 이 전혀 없는 단어(해당 유저가 처음 보는 단어)도 포함.
    - 단어 점수식 P = 0.6*R + 0.25*C + 0.15*D 로 상위 단어를 고르고,
      연결된 예문들을 모아 '단어 점수의 최대값' 순으로 정렬해서 반환.
    """
    now = datetime.now(timezone.utc)

    # 1) 단어 + (해당 유저의 스킬: 없으면 NULL) + 단어의 예문 연결수(deg)
    # 핵심: outerjoin(UserWordSkill, ON (word_id & user_id))
    stmt = (
        select(
            Word,
            UserWordSkill,
            func.count(WordExample.example_id).label("deg"),
        )
        .select_from(Word)
        .outerjoin(
            UserWordSkill,
            and_(
                UserWordSkill.word_id == Word.id,
                UserWordSkill.user_id == user_id,   # 반드시 ON 절에 둔다!
            ),
        )
        .outerjoin(WordExample, WordExample.word_id == Word.id)
        .group_by(Word.id, UserWordSkill.id)
    )

    rows = db.execute(stmt).all()  # List[Tuple[Word, UserWordSkill|None, deg]]

    # 2) 점수 계산 (스킬 없으면 "처음 보는 단어" 취급)
    tau0_sec = 7 * 24 * 3600  # 7일
    alpha = 1.5               # 숙련 반영 계수
    words_with_score: List[tuple[Word, float]] = []

    for word, skill, deg in rows:
        # skill_val: reading/listening/speaking 평균 (없으면 0)
        if skill is not None:
            skill_val = (skill.reading + skill.listening + skill.speaking) / 3.0
            updated_at = skill.updated_at or datetime(1970, 1, 1, tzinfo=timezone.utc)
        else:
            skill_val = 0.0
            updated_at = datetime(1970, 1, 1, tzinfo=timezone.utc)  # "아예 처음 보는" 효과

        dt_sec = (now - updated_at).total_seconds()
        tau = tau0_sec * (1 + alpha * skill_val)

        # R: 경과시간이 클수록 큼(숙련 높으면 tau↑ → 느리게 증가)
        R = 1 - math.exp(-dt_sec / tau) if tau > 0 else 1.0

        # C: 연결수(deg)가 작을수록 큼 + "처음 보는 단어" 보너스
        unseen_bonus = 0.3 if skill is None else 0.0
        C = (0.7 / (1 + math.log1p(deg or 0))) + unseen_bonus

        # D: 숙련 낮을수록 큼
        D = 1.0 - skill_val

        P = 0.6 * R + 0.25 * C + 0.15 * D
        words_with_score.append((word, P))

    # 3) 상위 단어 선택
    words_with_score.sort(key=lambda x: x[1], reverse=True)
    top_words = [w for w, _ in words_with_score[:max(1, limit_words)]]
    top_word_ids = [w.id for w in top_words]
    score_by_word_id: Dict[int, float] = {w.id: s for w, s in words_with_score}

    if not top_word_ids:
        return []

    # 4) 상위 단어와 연결된 예문을 모으되,
    #    예문이 여러 단어에 연결될 수 있으므로 "해당 예문에 연결된 단어 점수의 최대값"으로 정렬
    stmt_ex = (
        select(Example, WordExample.word_id)
        .join(WordExample, WordExample.example_id == Example.id)
        .where(WordExample.word_id.in_(top_word_ids))
    )
    pairs = db.execute(stmt_ex).all()  # List[Tuple[Example, int]]

    # 예문별 점수집계(최대값)
    example_best_score: Dict[int, float] = {}
    example_obj_by_id: Dict[int, Example] = {}

    for ex, w_id in pairs:
        example_obj_by_id[ex.id] = ex
        s = score_by_word_id.get(w_id, 0.0)
        if ex.id not in example_best_score or s > example_best_score[ex.id]:
            example_best_score[ex.id] = s

    # 5) 점수순 정렬 + 중복 제거 후 제한
    ranked_example_ids = sorted(example_best_score.keys(), key=lambda eid: example_best_score[eid], reverse=True)
    ranked_examples = [example_obj_by_id[eid] for eid in ranked_example_ids[:max(1, limit_examples)]]
    return ranked_examples