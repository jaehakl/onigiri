import math
import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple

from sqlalchemy import func, and_, select
from sqlalchemy.orm import Session

from db import Example, WordExample, Word, UserWordSkill

# ---- 유틸 -------------------------------------------------------------

def _cosine(u: Optional[List[float]], v: Optional[List[float]]) -> float:
    """코사인 유사도. 임베딩이 없으면 0.0."""
    if not u or not v:
        return 0.0
    s = sum(a*b for a, b in zip(u, v))
    nu = math.sqrt(sum(a*a for a in u))
    nv = math.sqrt(sum(b*b for b in v))
    if nu == 0 or nv == 0:
        return 0.0
    return s / (nu * nv)

def _gumbel() -> float:
    """Gumbel(0,1)"""
    u = random.random()
    # 보호 차원에서 underflow 방지
    u = min(max(u, 1e-12), 1 - 1e-12)
    return -math.log(-math.log(u))

def _mmr_select(
    candidates: List[Tuple[int, List[float]]],  # [(id, embedding)]
    query_vec: Optional[List[float]],
    k: int,
    lambda_rel: float = 0.7
) -> List[int]:
    """
    candidates에서 k개 인덱스를 MMR로 선택.
    query_vec이 None이면 관련성 항은 0으로 취급(=다양화만).
    반환값: 후보 리스트 내 인덱스(0..len-1)의 리스트
    """
    if not candidates or k <= 0:
        return []

    sims_to_q = [(_cosine(vec, query_vec) if query_vec else 0.0) for _, vec in candidates]
    picked: List[int] = []
    remaining = set(range(len(candidates)))

    while remaining and len(picked) < k:
        best_i, best_score = None, -1e9
        for i in list(remaining):
            rel = sims_to_q[i]
            if not picked:
                score = rel
            else:
                # 이미 고른 항목들과의 최대 유사도
                max_sim = max(_cosine(candidates[i][1], candidates[j][1]) for j in picked)
                score = lambda_rel * rel - (1 - lambda_rel) * max_sim
            if score > best_score:
                best_score, best_i = score, i
        picked.append(best_i)
        remaining.remove(best_i)
    return picked

# ---- 메인 함수 --------------------------------------------------------

def select_examples_for_user_randomized(
    db: Session,
    user_id: str,
    *,
    words_k: int = 10,                 # 고를 단어 수
    examples_per_word: int = 3,        # 단어당 예문 수
    total_examples: Optional[int] = None,  # 최종 개수 제한(없으면 words_k*examples_per_word)
    # 점수식 파라미터
    tau0_days: float = 7.0,
    alpha: float = 1.5,
    lambda_R: float = 0.6,
    lambda_C: float = 0.25,
    lambda_D: float = 0.15,
    unseen_bonus: float = 0.3,
    # 무작위/탐험
    temperature: float = 0.8,          # Gumbel-Top-k용 softmax 온도(작을수록 exploitation)
    word_mmr_lambda: float = 0.7,      # 단어 다양화 강도
    sent_mmr_lambda: float = 0.7,      # 예문 다양화 강도
    # 임베딩 필터
    gamma: float = 0.35,               # 단어–예문 코사인 하한
    # 상기(recall) 주입
    remind_prob: float = 0.08,
    hi_skill_threshold: float = 0.8,
    gap_days_for_remind: int = 14,
    # 안전장치
    per_word_candidate_cap: int = 80,  # 예문 후보 최대 조회 수
) -> List[Example]:
    """
    점수 기반 + 무작위 섞기 + 임베딩 MMR 다양화로 Example(예문) 목록을 반환.
    반환은 ORM Example 객체 리스트.
    """
    now = datetime.now(timezone.utc)
    tau0_sec = tau0_days * 24 * 3600

    # 1) 단어 + (해당 유저의 스킬: 없으면 NULL) + 단어의 예문 연결수(deg) + 임베딩
    stmt = (
        select(
            Word,
            # 해당 유저의 스킬만 왼쪽조인 (없으면 NULL)
            func.max(UserWordSkill.id).label("uws_id"),   # group_by를 간소화하기 위한 trick
            func.avg((UserWordSkill.reading + UserWordSkill.listening + UserWordSkill.speaking) / 3.0).label("skill_val"),
            func.max(UserWordSkill.updated_at).label("skill_updated_at"),
            func.count(WordExample.example_id).label("deg"),
        )
        .select_from(Word)
        .outerjoin(
            UserWordSkill,
            and_(
                UserWordSkill.word_id == Word.id,
                UserWordSkill.user_id == user_id,
            ),
        )
        .outerjoin(WordExample, WordExample.word_id == Word.id)
        .group_by(Word.id)
    )
    rows = db.execute(stmt).all()
    # rows: List[Tuple[Word, uws_id, skill_val, skill_updated_at, deg]]

    # 2) 단어 점수 계산
    word_items: List[Tuple[Word, float, float]] = []  # (Word, score P, skill_val)
    remind_pool_indices: List[int] = []
    for idx, (w, uws_id, skill_val, skill_updated_at, deg) in enumerate(rows):
        skill_val = float(skill_val) if skill_val is not None else 0.0
        updated_at = skill_updated_at or datetime(1970, 1, 1, tzinfo=timezone.utc)
        dt_sec = (now - updated_at).total_seconds()
        deg = int(deg or 0)

        tau = tau0_sec * (1 + alpha * skill_val)
        R = 1 - math.exp(-dt_sec / tau) if tau > 0 else 1.0
        C = (0.7 / (1 + math.log1p(deg))) + (unseen_bonus if uws_id is None else 0.0)
        D = 1.0 - skill_val

        P = lambda_R * R + lambda_C * C + lambda_D * D
        word_items.append((w, P, skill_val))

        # 상기 풀 후보
        if skill_val >= hi_skill_threshold and (now - updated_at) >= timedelta(days=gap_days_for_remind):
            remind_pool_indices.append(idx)

    if not word_items:
        return []

    # 3) Gumbel-Top-k로 무작위성 가미 + 임베딩 MMR로 단어 다양화
    #    (a) 스코어를 softmax(temperature)로 가중 → Gumbel 키 생성
    scores = [P for _, P, _ in word_items]
    s_min, s_max = min(scores), max(scores)
    # 정규화(수치 안정): 0..1
    norm = [(s - s_min) / (s_max - s_min + 1e-9) for s in scores]
    # softmax with temperature
    exps = [math.exp(x / max(temperature, 1e-6)) for x in norm]
    Z = sum(exps) + 1e-12
    weights = [x / Z for x in exps]
    # Gumbel key
    keys = [math.log(max(w, 1e-12)) + _gumbel() for w in weights]
    order = sorted(range(len(word_items)), key=lambda i: keys[i], reverse=True)

    #    (b) 단어-임베딩 MMR 선택
    # 단어 임베딩 모음
    word_vecs = [ (wi[0].id, list(wi[0].embedding) if wi[0].embedding is not None else None) for wi in word_items ]

    selected_word_idxs: List[int] = []
    candidate_set = order[:]  # Gumbel로 섞은 우선순위
    while candidate_set and len(selected_word_idxs) < words_k:
        best_idx, best_score = None, -1e9
        for i in candidate_set[: min(200, len(candidate_set))]:  # 과한 탐색 방지
            P_norm = norm[i]
            if not selected_word_idxs:
                score_i = P_norm
            else:
                # 이미 선택된 단어들과의 최대 코사인
                wid_i, vec_i = word_vecs[i]
                max_sim = 0.0
                if vec_i:
                    for j in selected_word_idxs:
                        _, vec_j = word_vecs[j]
                        max_sim = max(max_sim, _cosine(vec_i, vec_j))
                score_i = word_mmr_lambda * P_norm - (1 - word_mmr_lambda) * max_sim
            # 약간의 추가 Gumbel(아주 약하게)로 무작위성 유지
            score_i += 0.05 * _gumbel()
            if score_i > best_score:
                best_score, best_idx = score_i, i
        selected_word_idxs.append(best_idx)
        candidate_set.remove(best_idx)

    #    (c) 확률적으로 상기 풀에서 1~2개 주입(중복 피함)
    if remind_pool_indices and random.random() < remind_prob:
        random.shuffle(remind_pool_indices)
        for i in remind_pool_indices[:2]:
            if i not in selected_word_idxs:
                selected_word_idxs.append(i)
                if len(selected_word_idxs) >= words_k + 1:
                    break

    selected_words = [word_items[i][0] for i in selected_word_idxs]
    selected_word_ids = [w.id for w in selected_words]
    word_by_id = {w.id: w for w in selected_words}
    word_vec_by_id = {w.id: (list(w.embedding) if w.embedding is not None else None) for w in selected_words}

    # 4) 단어별 예문 후보 가져오기(+임베딩 필터 γ) → 예문 MMR로 k개 선택
    #    SQL에서 코사인 정렬도 가능하지만(벡터 opclass가 cosine일 때),
    #    여기서는 범용성을 위해 파이썬에서 유사도 계산/필터링한다.
    picked_examples: List["Example"] = []
    seen_example_ids: set[int] = set()

    for wid in selected_word_ids:
        # 해당 단어에 연결된 예문 후보
        stmt_ex = (
            select(Example)
            .join(WordExample, WordExample.example_id == Example.id)
            .where(WordExample.word_id == wid)
            .limit(per_word_candidate_cap)
        )
        cand_examples: List["Example"] = db.execute(stmt_ex).scalars().all()
        if not cand_examples:
            continue

        wvec = word_vec_by_id.get(wid)

        # (a) 단어–예문 코사인 유사도 계산 + γ 필터
        filtered: List[Tuple[int, List[float], "Example", float]] = []  # (idx, evec, obj, sim)
        for i, ex in enumerate(cand_examples):
            evec = list(ex.embedding) if ex.embedding is not None else None
            sim = _cosine(evec, wvec)
            if sim >= gamma or evec is None or wvec is None:
                filtered.append((i, evec, ex, sim))

        if not filtered:
            continue

        # (b) 예문 MMR 선택
        cand_for_mmr = [(i, evec) for (i, evec, _, _) in filtered]
        picked_idx_local = _mmr_select(cand_for_mmr, wvec, k=examples_per_word, lambda_rel=sent_mmr_lambda)

        # (c) 중복 제거 + 수집
        for i_local in picked_idx_local:
            _, _, ex_obj, _ = filtered[i_local]
            if ex_obj.id in seen_example_ids:
                continue
            picked_examples.append(ex_obj)
            seen_example_ids.add(ex_obj.id)

    # 5) 라운드로빈식 섞기(단어별로 1개씩 번갈아 넣는 interleave) — 위 루프에서 이미 가까운 형태
    # 최종 개수 제한
    if total_examples is None:
        total_examples = words_k * examples_per_word

    return picked_examples[:total_examples]
