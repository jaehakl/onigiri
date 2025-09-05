# auth.py
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session,  joinedload, selectinload
from sqlalchemy import select, update, func, text

from settings import settings
from utils.auth_utils import hash_token
from db import SessionLocal, User, UserRole, Session as DbSession   # DbSession = 세션 테이블

# 공용 DB 의존성(이미 deps.py가 있다면 그걸 써도 됩니다)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CurrentUser:
    """
    라우터에서 필요한 최소 정보만 담아 반환.
    필요하면 pydantic BaseModel로 바꿔도 됩니다.
    """
    def __init__(self, id: str, email: str | None, display_name: str | None, picture_url: str | None, roles: list[str]):
        self.id = id
        self.email = email
        self.display_name = display_name
        self.picture_url = picture_url
        self.roles = roles


TOUCH_INTERVAL_MIN = 5

def _maybe_touch_last_seen(db: Session, sess_id: str):
    # last_seen_at이 N분보다 오래됐을 때만 갱신
    db.execute(
        update(DbSession)
        .where(
            DbSession.id == sess_id,
            # PostgreSQL
            DbSession.last_seen_at < func.now() - text(f"interval '{TOUCH_INTERVAL_MIN} minutes'")
        )
        .values(last_seen_at=func.now())
    )
    db.commit()

def _load_user_from_session_cookie(request: Request, db: Session) -> User:
    cookie_name = settings.session_cookie_name
    raw = request.cookies.get(cookie_name)
    if not raw:
        raise HTTPException(status_code=401, detail="no session")

    sid_hash = hash_token(raw)

    # 세션과 유저를 한 번에, 그리고 roles까지 eager load
    stmt = (
        select(DbSession)
        .options(
            joinedload(DbSession.user).options(
                selectinload(User.user_roles).joinedload(UserRole.role)
            )
        )
        .where(
            DbSession.session_id_hash == sid_hash,
            DbSession.revoked_at.is_(None),
        )
        .limit(1)
    )
    sess = db.scalars(stmt).first()
    if not sess or not sess.user or not getattr(sess.user, "is_active", True):
        raise HTTPException(status_code=401, detail="invalid session")

    # last_seen Throttling (아래 #4 참고)
    _maybe_touch_last_seen(db, sess.id)

    return sess.user

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> CurrentUser | None:
    """
    라우터에서 Depends(get_current_user) 로 사용.
    인증 실패 시 401을 던집니다.
    인증이 선택인 엔드포인트에서 사용. 세션 없으면 None 반환.
    """
    try:
        print(1)
        user = _load_user_from_session_cookie(request, db)
        print(2)
    except HTTPException:
        return None

    roles = []
    if hasattr(user, "user_roles") and user.user_roles:
        roles = [ur.role.name for ur in user.user_roles if hasattr(ur, "role") and ur.role]
    return CurrentUser(
        id=str(user.id),
        email=user.email,
        display_name=getattr(user, "display_name", None),
        picture_url=getattr(user, "picture_url", None),
        roles=roles,
    )


