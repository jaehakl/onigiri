# 🍙 Onigiri - 일본 노래 가사 단어 학습기

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.0+-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**사용자가 좋아하는 일본 노래 가사를 기반으로, 개인의 학습 목적과 수준에 맞춰 동적으로 생성되는 맞춤형 일본어 학습 경험을 제공하는 웹 서비스**

## ✨ 주요 기능

### 🎵 가사 분석 및 맞춤형 교재 생성
- 일본어 텍스트(가사 등) 자유 입력 및 분석
- 포함된 모든 학습 대상 단어 자동 추출
- 사용자 학습 이력 기반 개인 맞춤형 학습 세션 생성
- **[노래 제목] 마스터하기** 형태의 교재 자동 생성

### 📚 단어 상세 정보 제공
- **일본어 표기**: 한자, 히라가나/가타카나
- **발음**: 히라가나/가타카나 표기 및 원어민 음성
- **한국어 뜻**: 핵심 의미 제공
- **상징 이미지**: AI 생성 고유 이미지
- **맞춤 예문**: 학습 목적별 태깅된 예문 세트

### 🎮 게이미피케이션 기반 퀴즈 시스템
- **다양한 퀴즈 유형**:
  - 단어 ↔ 뜻 맞히기 (객관식/단답형)
  - 단어 ↔ 발음 맞히기 (객관식/단답형)
  - 단어 ↔ 이미지 연결하기 (객관식)
  - 예문 빈칸 채우기 (객관식/단답형)
  - 예문 듣고 빈칸 채우기 (객관식)
  - 단어 배열하여 문장 완성하기
  - 예문 ↔ 뜻 번역하기 (자기 주도 채점)
- 즉각적인 정답/오답 피드백 및 해설

### 📊 개인 학습 대시보드
- **종합 능력치 차트**: 어휘력, 문법, 청해력, 독해력, 속도
- **분야별 숙련도**: JLPT 급수, 학습 목적, 품사별 진행도
- **학습 습관 트래킹**: 학습 캘린더(잔디), 연속 학습일
- **누적 성장 그래프**: 총 학습 단어 수 변화

## 🏗️ 기술 스택

### Backend
- **Python 3.11+** - 메인 프로그래밍 언어
- **FastAPI** - 고성능 웹 프레임워크
- **SQLAlchemy 2.0** - ORM 및 데이터베이스 관리
- **PostgreSQL** - 메인 데이터베이스
- **Poetry** - 의존성 관리
- **Uvicorn** - ASGI 서버

### Frontend
- **React 19** - 사용자 인터페이스
- **Vite** - 빌드 도구 및 개발 서버
- **RSuite** - UI 컴포넌트 라이브러리
- **React Router** - 클라이언트 사이드 라우팅
- **Recharts** - 데이터 시각화
- **Axios** - HTTP 클라이언트

### AI/ML
- **Fugashi + Unidic** - 일본어 형태소 분석
- **Stable Diffusion** - 이미지 생성
- **TTS (VITS, Coqui TTS)** - 음성 합성
- **LLM API** - 예문 생성

### Infrastructure
- **AWS S3** - 파일 스토리지
- **Nginx** - 리버스 프록시 및 정적 파일 서빙
- **Google OAuth 2.0** - 사용자 인증
- **Let's Encrypt** - SSL 인증서

## 🚀 빠른 시작

### 사전 요구사항
- Python 3.11+
- Node.js 18+ (LTS 권장)
- PostgreSQL 13+
- Poetry
- pnpm

### 1. 저장소 클론
```bash
git clone https://github.com/jaehakl/onigiri.git
cd onigiri
```

### 2. Backend 설정
```bash
cd apps/jpkr/api
poetry install
cp .env.example .env
# .env 파일에서 데이터베이스 및 API 키 설정
poetry run uvicorn app.main:app --reload
```

### 3. Frontend 설정
```bash
cd apps/jpkr/ui
pnpm install
cp .env.example .env
# .env 파일에서 API 엔드포인트 설정
pnpm run dev
```

### 4. 데이터베이스 설정
```bash
# PostgreSQL 데이터베이스 생성
createdb onigiri

# 환경 변수 설정 후 마이그레이션 실행
poetry run python -m alembic upgrade head
```

## 📁 프로젝트 구조

```
onigiri/
├── apps/
│   └── jpkr/                    # 일본어-한국어 앱
│       ├── api/                 # FastAPI 백엔드
│       │   ├── app/
│       │   │   ├── models.py    # 데이터베이스 모델
│       │   │   ├── routers/     # API 라우터
│       │   │   ├── service/     # 비즈니스 로직
│       │   │   └── utils/       # 유틸리티 함수
│       │   ├── pyproject.toml   # Python 의존성
│       │   └── .env             # 환경 변수
│       └── ui/                  # React 프론트엔드
│           ├── src/
│           │   ├── components/  # 재사용 가능한 컴포넌트
│           │   ├── pages/       # 페이지 컴포넌트
│           │   ├── contexts/    # React Context
│           │   └── service/     # API 서비스
│           ├── package.json     # Node.js 의존성
│           └── vite.config.js   # Vite 설정
├── deployment/                   # 배포 관련 파일
├── docs/                        # 프로젝트 문서
└── README.md                    # 프로젝트 개요
```

## 🔧 개발 환경 설정

### Backend 개발
```bash
cd apps/jpkr/api
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend 개발
```bash
cd apps/jpkr/ui
pnpm install
pnpm run dev
```

### 데이터베이스 마이그레이션
```bash
cd apps/jpkr/api
poetry run alembic revision --autogenerate -m "Description"
poetry run alembic upgrade head
```

## 🌐 배포

### 프로덕션 배포 가이드
자세한 배포 방법은 [deployment/deployment.md](deployment/deployment.md)를 참조하세요.

### 주요 배포 단계
1. **Lightsail 인스턴스 생성** 및 고정 IP 설정
2. **도메인 연결** 및 DNS 설정
3. **Nginx 리버스 프록시** 구성
4. **HTTPS 인증서** 설정 (Let's Encrypt)
5. **systemd 서비스**로 백엔드 자동 실행

## 📖 API 문서

### 주요 엔드포인트
- `POST /words/create/batch` - 단어 일괄 생성
- `POST /examples/create/batch` - 예문 일괄 생성
- `POST /words/personal/create` - 개인 단어 생성
- `GET /words/search/{search_term}` - 단어 검색
- `POST /text/analyze` - 텍스트 분석

### 인증
Google OAuth 2.0을 통한 사용자 인증 시스템을 제공합니다.

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 👥 팀

- **Jaehak Lee** - [leejaehak87@gmail.com](mailto:leejaehak87@gmail.com)

## 📞 지원

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해 주세요.

---

**🍙 Onigiri** - 일본어 학습을 더욱 즐겁고 효과적으로 만들어 드립니다!
