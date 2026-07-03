# FitNote Trainer

헬스트레이너가 회원별 수업 기록, 자세 분석 결과, 피드백, 과제를 관리할 수 있도록 돕는 헬스케어 미니 프로젝트입니다.

FastAPI + Next.js 기반 실제 웹앱(트레이너용 관리 도구 / 회원용 모바일 포털 완전 분리)과, 별도로 수업 제출용 Gradio 프로토타입을 함께 포함합니다.

## Current Artifacts

- `backend/`: FastAPI + SQLite 백엔드 (실제 웹앱)
- `frontend/`: Next.js 프론트엔드 (트레이너/회원 분리, 실제 웹앱)
- `fitnote-trainer-prd.md`: PRD 정리 문서
- `fitnote-trainer-erd-table-candidates.md`: ERD 테이블 후보 정리
- `fitnote-trainer-gradio-screen-flow.md`: 화면 흐름 정리 (6탭 구성 기준 문서)
- `fitnote-trainer-erdcloud-import.sql`: ERDCloud import용 SQL (DB 설계 기준 문서)
- `fitnote-trainer-erdcloud-logical-name-map.csv`: ERDCloud 논리명 매핑표
- `fitnote-trainer-colab-sample-queries.py`: Colab 샘플 데이터 및 분석 쿼리
- `gradio_app.py`: FitNote Trainer Gradio 대시보드 프로토타입 (수업 제출용)
- `ai_service.py`: OpenAI API 기반 세션 요약/리포트 생성 서비스, API 키가 없으면 fallback
- `pose_service.py`: Ultralytics YOLO pose 기반 자세 분석 서비스, YOLO 사용 불가 시 fallback
- `.env.example`: Gradio 프로토타입용 OpenAI/YOLO 실행 환경변수 예시
- `backend/.env.example`: FastAPI 백엔드용 OpenAI/YOLO 환경변수 예시
- `CLAUDE_HANDOFF.md`: 실제 웹앱 구현 시작용 인수인계 문서
- `Healthcare_MiniProject_Guide.pdf`: 프로젝트 가이드
- `헬스케어_FitNote_5.기능요구사항_추가기능반영.xlsx - 5.기능요구사항.csv`: 기능 요구사항 CSV

## Run the Web App (FastAPI + Next.js)

### 1. Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py          # 데모 데이터 생성 (트레이너 1명 + 회원 3명)
.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend (다른 터미널에서)

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 `http://localhost:3000` 접속.

### 데모 로그인 정보 (seed.py 실행 기준)

- 트레이너: 아이디 `trainer1` / 비밀번호 `pass1234`
- 회원: 이름 `박수진` / 전화번호 뒷자리 `5678` (또는 `이민호`/`3333`, `최유나`/`4444`)

### 구조

- 트레이너 화면: `/trainer/*` — 데스크탑은 좌측 사이드바(관리 도구 형태), 모바일은 하단 탭바
- 회원 화면: `/member/*` — 모바일 우선 포털, 데스크탑은 중앙 정렬된 좁은 레이아웃
- 로그인: `/login` — 트레이너/회원 탭 전환
- `next.config.ts`의 rewrites가 `/api/*`, `/uploads/*`를 백엔드(`BACKEND_ORIGIN`, 기본 `http://127.0.0.1:8000`)로 프록시합니다.

### 자세 분석 / AI

현재 backend와 Gradio는 OpenAI API / YOLO pose를 optional로 사용합니다.

- `OPENAI_API_KEY`가 있으면 세션 메모 요약과 리포트 생성에 OpenAI API를 사용합니다.
- `ultralytics`와 YOLO pose 모델을 사용할 수 있으면 자세 이미지 분석 시 keypoint를 추출합니다.
- API 키, 패키지, 모델이 없거나 추론이 실패하면 fallback 분석으로 앱이 계속 동작합니다.

관련 파일:

- `backend/app/services/ai_service.py`
- `backend/app/services/pose_service.py`
- `backend/app/services/mock_ai.py`
- `ai_service.py`
- `pose_service.py`

API 키 설정은 두 가지 방식 중 하나를 사용하면 됩니다.

1. 환경변수 또는 `.env` 사용

```bash
# FastAPI 백엔드용 (backend/.env)
cp backend/.env.example backend/.env

# 또는 셸 환경변수로 직접 지정
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4o-mini"
export YOLO_POSE_MODEL="yolov8n-pose.pt"
```

`backend/.env`는 `backend/app/services/ai_service.py`, `pose_service.py`가 자동으로 읽습니다. 값을 비워두거나 파일이 없어도 규칙 기반 fallback으로 정상 동작합니다.

2. 코드 파일에 직접 입력

```bash
cp local_secrets.example.py local_secrets.py
```

이후 `local_secrets.py`에 직접 입력합니다.

```python
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4o-mini"
```

`local_secrets.py`는 `.gitignore`에 포함되어 있어 GitHub에 올라가지 않습니다. Gradio와 FastAPI 백엔드가 모두 이 파일을 읽습니다.

## Run Gradio Dashboard (수업 제출용 프로토타입)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python gradio_app.py
```

실행 후 브라우저에서 `http://127.0.0.1:7860`으로 접속합니다.

### Gradio AI / YOLO 연동

Gradio 프로토타입은 아래 순서로 동작합니다.

- `OPENAI_API_KEY`가 있으면 Tab 3의 텍스트 기반 음성 메모 요약과 Tab 4의 회원 리포트 생성에 OpenAI API를 사용합니다.
- `ultralytics`와 YOLO pose 모델을 사용할 수 있으면 자세 이미지 업로드 시 keypoint를 추출합니다.
- API 키가 없거나 YOLO 추론이 실패하면 규칙 기반 fallback으로 앱이 계속 동작합니다.

환경변수 예시는 `.env.example`, 직접 입력 예시는 `local_secrets.example.py`를 참고하세요.

```bash
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4o-mini"
export YOLO_POSE_MODEL="yolov8n-pose.pt"
.venv/bin/python gradio_app.py
```

## Planned Flow

1. PRD 확정
2. 화면 구성 확정
3. ERD 설계
4. SQLite 테이블 생성
5. 샘플 데이터 적재
6. Gradio 프로토타입 구현 (수업 제출용)
7. FastAPI + Next.js 실제 웹앱 구현 (포트폴리오 확장)
