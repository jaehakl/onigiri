from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
import requests

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from settings import settings
from db import SessionLocal  # 기존 db.py 모델 임포트

from user_auth.db import OAuthState, User, Identity, UserRole, Role
from models import UserData
from user_auth.utils.auth_utils import random_urlsafe, pkce_challenge, set_return_to_cookie, pop_return_to_cookie
from user_auth.utils.jwt import make_access, make_refresh, verify_token

router = APIRouter(prefix="/auth", tags=["auth"])

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = "openid email profile"
PROVIDER = "google"

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# 로그인 시작
@router.get("/google/start")
def google_start(request: Request, return_to: str | None = None, db: Session = Depends(get_db)):
    state = random_urlsafe(32)
    nonce = random_urlsafe(32)
    code_verifier = random_urlsafe(64)
    challenge = pkce_challenge(code_verifier)

    st = OAuthState(
        provider=PROVIDER,   # Enum을 쓰면 OAuthProvider.google
        state=state,
        nonce=nonce,
        code_verifier=code_verifier,
        redirect_uri=settings.google_redirect_uri,
    )
    db.add(st)
    db.commit()

    # 사용자가 눌렀던 페이지로 되돌아가기 위해 임시 쿠키에 저장
    resp = RedirectResponse(url="/")
    set_return_to_cookie(resp, return_to)

    from urllib.parse import urlencode
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
        "nonce": nonce,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "access_type": "offline",   # refresh_token 필요 시
        # "prompt": "consent",
    }
    resp.headers["Location"] = f"{AUTH_URL}?{urlencode(params)}"
    resp.status_code = 307
    return resp

# 콜백
@router.get("/google/callback")
def google_callback(request: Request, state: str = "", code: str = "", db: Session = Depends(get_db)):
    if not state or not code:
        raise HTTPException(400, "missing state or code")

    st = db.scalar(select(OAuthState).where(OAuthState.state == state))
    if not st or st.consumed_at is not None:
        raise HTTPException(400, "invalid or used state")

    # 토큰 교환
    data = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": st.redirect_uri or settings.google_redirect_uri,
        "grant_type": "authorization_code",
        "code_verifier": st.code_verifier,
    }
    tok = requests.post(TOKEN_URL, data=data, timeout=10)
    if tok.status_code != 200:
        raise HTTPException(400, f"token exchange failed: {tok.text}")
    token_json = tok.json()
    id_tok = token_json.get("id_token")
    expires_in = token_json.get("expires_in")

    # ID 토큰 검증
    try:
        req = google_requests.Request()
        idinfo = google_id_token.verify_oauth2_token(id_tok, req, settings.google_client_id)
        # nonce는 직접 확인
        if st.nonce and idinfo.get("nonce") != st.nonce:
            raise ValueError("nonce mismatch")
    except Exception as e:
        raise HTTPException(400, f"id_token verification failed: {e}")

    sub = idinfo["sub"]
    email = idinfo.get("email")
    email_verified = bool(idinfo.get("email_verified", False))
    name = idinfo.get("name")
    picture = idinfo.get("picture")

    # 아이덴티티 조회/생성
    ident = db.scalar(select(Identity).where(Identity.provider == PROVIDER, Identity.provider_user_id == sub))
    if ident:
        user = db.get(User, ident.user_id)
    else:
        user = None
        if email and email_verified:
            # CITEXT면 == email, TEXT면 lower 비교 등으로 수정
            user = db.scalar(select(User).where(User.email == email))
        if not user:
            user = User(
                email=email,
                email_verified_at=func.now() if email_verified else None,
                display_name=name,
                picture_url=picture,
                is_active=True,
            )
            db.add(user)
            db.flush()  # user.id 확보

        # 기본 "user" 역할 추가
        user_role = db.scalar(select(Role).where(Role.name == "user"))
        if not user_role:
            # "user" 역할이 없으면 생성
            user_role = Role(name="user")
            db.add(user_role)
            db.flush()  # role.id 확보
        
        user_role_entry = UserRole(user_id=user.id, role_id=user_role.id)
        db.add(user_role_entry)

        ident = Identity(
            user_id=user.id,
            provider=PROVIDER,
            provider_user_id=sub,
            email=email,
            email_verified=email_verified,
            raw_profile=idinfo,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=expires_in or 0) if expires_in else None,
            scope=token_json.get("scope", "").split() if token_json.get("scope") else None,
        )
        db.add(ident)

    # state 소진
    st.consumed_at = func.now()

    # 3) 내부 JWT 생성
    access = make_access(user)
    refresh = make_refresh(str(user.id))

    # 돌아갈 곳
    return_to = request.cookies.get("rt") or settings.app_base_url
    resp = RedirectResponse(return_to)

    # 4) 쿠키/바디로 전달
    set_auth_cookies(resp, access, refresh)

    pop_return_to_cookie(resp)
    return resp


@router.get("/me")
def check_user(request: Request, db: Session = Depends(get_db))->UserData:

    token = request.cookies.get("access_token")

    # 2) 없으면 Authorization 헤더 (Bearer …) 시도
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        claims = verify_token(token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}")

    user_data = UserData(
        id=str(claims.get("sub")),
        email=claims.get("email"),
        display_name=claims.get("display_name"),
        picture_url=claims.get("picture_url"),
        roles=claims.get("roles"),
    )
    if not user_data.id:
        raise HTTPException(status_code=401, detail="Token missing sub")
    return user_data


@router.get("/refresh")
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    rtoken = request.cookies.get("refresh_token")
    if not rtoken:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        claims = verify_token(rtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid refresh: {e}")

    if claims.get("typ") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    user_id = claims["sub"]
    user = db.query(User).get(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive")

    # (선택) 토큰 로테이션/블록리스트 검사·등록

    access = make_access(user)
    refresh_new = make_refresh(user_id)   # 로테이션 권장

    # 쿠키 갱신
    kwargs = {"httponly": True, "secure": settings.SECURE_COOKIES, "samesite": "lax", "domain": settings.COOKIE_DOMAIN}
    response.set_cookie("access_token", access, max_age=settings.ACCESS_TTL_SEC, path="/", **kwargs)
    response.set_cookie("refresh_token", refresh_new, max_age=settings.REFRESH_TTL_SEC, path="/", **kwargs)
    return {"ok": True}


@router.post("/logout")
def logout(resp: Response):
    kwargs = {"httponly": True, "secure": settings.SECURE_COOKIES, "samesite": "lax", "domain": settings.COOKIE_DOMAIN}
    resp.delete_cookie("access_token", path="/", **kwargs)
    resp.delete_cookie("refresh_token", path="/", **kwargs)
    return {"ok": True}

def set_auth_cookies(resp: Response, access: str, refresh: str):
    kwargs = {"httponly": True, "secure": settings.SECURE_COOKIES, "samesite": "lax", "domain": settings.COOKIE_DOMAIN}
    resp.set_cookie("access_token", access, max_age=settings.ACCESS_TTL_SEC, path="/", **kwargs)
    resp.set_cookie("refresh_token", refresh, max_age=settings.REFRESH_TTL_SEC, path="/", **kwargs)
