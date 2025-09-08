
# Onigiri - 전자 일본어 학습기

[https://www.onigiri.kr/](https://www.onigiri.kr/)

# 개요
**핵심 기능 (Core Features)**
- 문장 학습 모드(feed_examples)
	- 추천 알고리즘에 따라 사용자에게 적합한 예문을 6개씩 제공
		- 형태소 분석 기반 단어 하이라이트, 삽화/음성, 한국어 뜻 제공
		- 삽화를 누르면 음성 재생, 한국어 뜻은 버튼으로 토글
- 텍스트 분석(Analysis_text)
	- 스크립트/유튜브 URL 저장 후 불러오기
	- 텍스트에서 자동으로 단어 추출 및 난이도/숙련도 표시
		- 단어 클릭으로 상호작용(개인 숙련도 업데이트 → 추후 낮은 숙련 위주 표시)
- 개인 단어/예문 관리 및 CRUD
	- DB에 단어가 없거나 잘못된 경우, 직접 저장 가능(본인 데이터 우선 표시)
- 학습 진행도 모니터링(사용자 요약/상세 데이터)

# 시스템 아키텍처
- 백엔드: FastAPI + SQLAlchemy, PostgreSQL(+pgvector), JWT 쿠키, Google OAuth
- 프런트엔드: Vite + React(rsuite UI)
- Creator: 로컬 전용 생성/관리 서버(임베딩/오디오/이미지/중복처리)
- 배포: Nginx 리버스 프록시, systemd 서비스, Certbot SSL

# 레포 디렉터리 개요
- `apps/jpkr/api/app`: 메인 백엔드(FastAPI)
	- `main.py`: API 엔드포인트
	- `initserver.py`: CORS/DB 확장/라우터 초기화
	- `settings.py`: 환경변수 설정
	- `db.py`: DB 엔진/세션/앱 도메인 모델(`Word`, `Example`, `UserWordSkill`, `UserText`...)
	- `user_auth/*`: 사용자/역할/아이덴티티/세션, OAuth, JWT 발급/검증
	- `service/*`: 비즈니스 로직(단어/예문/텍스트/추천/분석/S3 등)
	- `methods/*`: 다양한 추천 알고리즘 구현
- `apps/jpkr/ui`: 프런트엔드(React)
- `apps/jpkr/api/app/_creator`: Creator 전용 백엔드(로컬 관리/생성)
- `deployment/*`: Nginx/systemd/업데이트 스크립트 문서
- `docs/*`: 추가 문서(로드맵/콘텐츠 등)

# 빠른 시작(로컬 개발)
## 필수 요구사항
- Python >= 3.11
- Node.js >= 18, pnpm 또는 npm
- PostgreSQL(권장, pgvector 확장 필요). SQLite로도 기동은 가능하나 벡터/추천 일부 기능 제한

## 환경변수(.env 예시)
백엔드 `apps/jpkr/api/app/.env`
```env
ONIGIRI_DB_URL=postgresql+psycopg://user:pass@localhost:5432/onigiri
APP_BASE_URL=http://localhost:5173

# OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# JWT
JWT_SECRET=change_me
COOKIE_DOMAIN=localhost

# AWS S3 (옵션: 오디오/이미지 프리사인 URL)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-northeast-2
S3_BUCKET=...
S3_ENDPOINT_URL=
```

프런트엔드 `apps/jpkr/ui/.env`
```env
VITE_API_BASE_URL=http://localhost:8000
```

## 초기 설치
1) 백엔드(Windows 예시)
```bat
cd apps\jpkr\api\app
poetry install
python -m unidic download
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2) 프런트엔드
```bat
cd apps\jpkr\ui
pnpm i
pnpm dev
```

3) 편의 스크립트(Windows)
- 루트의 `run.bat` 실행 시, 백엔드/프런트 각각 새 창으로 기동
- 프런트의 `apps/jpkr/ui/run.bat`는 브라우저를 열고 개발 서버 실행

# 인증/권한
- 로그인 흐름: `/auth/google/start` → Google → `/auth/google/callback`
- 내부 JWT(access/refresh)를 쿠키에 저장. `/auth/me`로 사용자 정보 확인
- 역할: `admin`, `user` (공개 엔드포인트는 `['*']` 허용)
- 토큰 만료 시 클라이언트는 `/auth/refresh` 재시도로 자동 복구(프런트 API 래퍼 참고)

# 주요 API 개요(발췌)
- Words(관리자): 생성/수정/삭제/전체/검색/필터 `/words/*`
- Examples(관리자): 생성/수정/삭제/필터 `/examples/*`
- 개인 단어: `/words/create/personal`, `/words/personal/random/{limit}`
- 사용자 텍스트: `/user_text/*` (create/get/all/update/delete)
- 사용자 데이터: `/user_admin/*`, `/user_data/*`
- 텍스트 분석: `/text/analyze` (형태소 분석 + 단어 매핑)
- 학습용 예문 추천: `/examples/get-examples-for-user`

# 추천 알고리즘 요약
- 기본 무작위: `methods/recommend_examples_simple.py`
- 점수 기반(SQL): `recommend_examples_fast.py`, `recommend_examples_fast_light.py`
- Python MMR 다양화: `recommend_examples_advanced.py`, `recommend_examples.py`
- 응답 전처리: `methods/words_from_examples_batch.py`가 예문 내 단어/숙련 정보 묶음

# 텍스트 분석(형태소)
- `utils/words_from_text.py`에서 Fugashi+Unidic 사용
	- 최초 사용 전 사전 다운로드 필요: `python -m unidic download`
- `service/analysis_text.py`가 DB의 `Word/Skill`과 매핑하여 라인/단어별 결과 제공

# Creator 앱(로컬 전용)
- 기능: 임베딩 생성(Sentence-Transformers), 예문 오디오(ESPnet TTS), 이미지(SDXL), 중복 단어 조회/병합, 유사도 조회(pgvector)
- 라우트: `_creator_main.py` 참조(관리자 전용 엔드포인트)
- 환경: CUDA/torch/flash_attn 등 호환 버전 필요(상세는 `_creator/README.md` 가이드)

# 배포 개요
- 문서: `deployment/deployment.md` 참고
	- Nginx 리버스 프록시(`/api/` → 127.0.0.1:8000), 정적 파일(`/var/www/app/dist`) 서빙
	- SSL: Certbot
	- systemd 서비스 예시 포함(uvicorn)
- 프런트 빌드 산출물: `apps/jpkr/ui` → `dist/` → `/var/www/app/dist/`로 동기화

# 데이터베이스/확장
- 권장: PostgreSQL + `pgvector`, `citext`, `pgcrypto`
	- 앱 기동 시 `initserver`에서 `CREATE EXTENSION IF NOT EXISTS` 시도
	- 권한 필요. 미설치 시 임베딩/유사도, 일부 인덱스 기능 제한
- 개발 편의를 위한 SQLite 기본값이 있으나, 추천/벡터 기능은 제한됨

# S3 연동(옵션)
- `utils/aws_s3.py`로 업로드/프리사인/삭제 지원
- 예문 오디오/이미지는 private 저장 후 presigned URL로 접근

# 컨텐츠 추가 Workflow
1. 메인 앱에서 관리자 계정으로 예문(태그/일본어/한국어/이미지 프롬프트) 입력
2. Creator 앱에서 임베딩 없는 단어 조회 → 임베딩 생성
3. Creator 앱에서 임베딩 없는 예문 조회 → 임베딩 생성
4. Creator 앱에서 오디오 없는 예문 조회 → 오디오 생성
5. Creator 앱에서 이미지 없는 예문 조회 → 이미지 생성

# 주의 및 알려진 이슈(개발 메모)
- PostgreSQL 확장 미설치 시 추천/유사도 기능이 제한될 수 있음
- 프런트 `apps/jpkr/ui/src/api/api.js`의 401 처리 시 `err.response?.status` 사용 권장
- 일부 CRUD 코드가 과거 스키마 명칭을 참조할 수 있으니(예: 단어 필드명) 실제 모델(`db.Word`)과 동기화 필요

# 라이선스
- MIT License