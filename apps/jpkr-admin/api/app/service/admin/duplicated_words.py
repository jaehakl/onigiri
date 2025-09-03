from typing import Dict, List, Optional, Set
from sqlalchemy import select, and_, func, exists
from sqlalchemy.orm import Session, selectinload
from collections import defaultdict


from db import Word  # SQLAlchemy ORM model

def get_duplicated_words(db: Session, user_id: Optional[str] = None) -> Dict[str, List[dict]]:
    """
    root_word_id가 NULL이 아닌 모든 단어들을, 최상위 root별로 묶어서
    { 'root word (ID: xxx)': [branch1_dict, branch2_dict, ...], ... } 형태로 반환.
    DB 왕복을 최소화하여 빠르게 수행.
    """

    # 1) Word 객체 전체를 로드하고 user 관계도 함께 로드
    base_stmt = select(Word)
    stmt_branches = base_stmt.where(Word.root_word_id.is_not(None))

    rows_branches = db.execute(stmt_branches).all()

    # 2) 인메모리 인덱스 구성
    #    - words_by_id: id -> row dict
    #    - children: parent_id -> [child_id...]
    words_by_id: Dict[str, dict] = {}
    children = defaultdict(list)
    has_parent: Set[str] = set()

    def row_to_dict(r) -> dict:
        # r는 Word 객체이므로 속성에 직접 접근
        return {
            'id': r.id,
            'root_word_id': r.root_word_id,
            'word': r.word,
            'jp_pronunciation': r.jp_pronunciation,
            'kr_pronunciation': r.kr_pronunciation,
            'kr_meaning': r.kr_meaning,
            'level': r.level,
            'user_id': r.user.id if r.user else None,
            'user_name': r.user.display_name if r.user else None,
            'created_at': r.created_at.isoformat() if r.created_at else None,
            'updated_at': r.updated_at.isoformat() if r.updated_at else None,
        }

    for r in rows_branches:
        d = row_to_dict(r[0])
        words_by_id[d['id']] = d
        if d['root_word_id']:
            children[d['root_word_id']].append(d['id'])
            has_parent.add(d['id'])

    stmt_roots = base_stmt.where(
        and_(
            Word.root_word_id.is_(None),
            Word.id.in_(children.keys())
        )
    )
    rows_roots = db.execute(stmt_roots).all()

    # 5) 각 루트마다 하위 전체 수집 (DFS/BFS)
    def collect_descendants(root_id: str) -> List[dict]:
        out: List[dict] = []
        stack = list(children[root_id])  # 루트의 '직계 자식'부터 시작
        visited: Set[str] = set()
        while stack:
            cid = stack.pop()
            if cid in visited:
                continue
            visited.add(cid)
            node = words_by_id.get(cid)
            if node:
                out.append(node)
                # 이 노드의 자식들을 스택에 추가
                if cid in children:
                    stack.extend(children[cid])
        return out

    groups: Dict[str, List[dict]] = {}
    # 6) key는 "word (ID: xxx)" 포맷으로
    for row in rows_roots:
        root = row_to_dict(row[0])
        if not root:
            continue
        key = f"{root['word']} (ID: {root['id']})"
        groups[key] = collect_descendants(root['id'])
        groups[key].append(root)

    return groups