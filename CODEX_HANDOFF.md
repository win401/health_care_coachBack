# FitNote Trainer — Codex 인수인계 문서

Claude(Cowork)에서 여기까지 작업했고, 토큰 소진으로 Codex로 작업을 이어갑니다. 이
문서는 "지금 실제로 뭐가 되어 있는지"를 정확히 반영한 스냅샷입니다. 루트의
`CLAUDE_HANDOFF.md`는 Gradio 프로토타입 단계에서 쓴 기획 문서라 지금은 상당 부분
낡았으니(실제 웹앱 구현 전 작성됨) 참고만 하고 이 문서를 우선으로 보세요.

## ⚠️ 시작 전 필수 확인

**이 문서에서 설명하는 최근 변경사항(민트 테마, 카메라/음성 녹음, 배포 준비)이 실제로
GitHub에 커밋/푸시됐는지 먼저 `git status`, `git log`로 확인하세요.** Claude 세션
마지막에 push 상태를 재확인하지 못했습니다. 로컬 워킹 디렉토리에는 분명히 반영되어
있지만(아래 "최근 변경 파일" 목록 참고), 커밋 여부는 다시 확인이 필요합니다.

## 1. 프로젝트 개요

- 이름: FitNote Trainer — PT 트레이너용 회원 관리 / 수업 기록 / 자세 분석 / 리포트 웹앱
- 원래 수업 과제(Gradio 제출)에서 방향 전환: **실제 FastAPI + Next.js 웹앱**으로 확장 구현하기로 결정 (Gradio 프로토타입은 `gradio_app.py`로 별도 보존, 제출용)
- 저장소 위치: `/Users/sungwoo/Desktop/work/class/mini_pj/health_care_coachBack`
- GitHub: `https://github.com/win401/health_care_coachBack.git` (브랜치 `main`)

## 2. 현재 상태 요약

**백엔드(`backend/`, FastAPI + raw sqlite3, ORM 없음)**와 **프론트엔드(`frontend/`,
Next.js 16 App Router)** 둘 다 완전히 구현되어 로컬에서 정상 동작 확인됨.

- 트레이너 로그인(아이디/비번) / 회원 로그인(이름+전화번호 뒷4자리) 완전 분리
- 트레이너 화면: 홈 대시보드(+Daily Schedule 일정표), 회원 목록/등록, 세션 기록(운동
  기록, 음성 메모 요약, 자세 사진 분석, 피드백, 과제 등록), 리포트 생성
- 회원 화면: 프로필 요약, 과제 확인, 일정, 진행 기록(자세 점수/몸무게 변화)
- 반응형: 데스크탑은 좌측 사이드바(관리 도구형), 모바일은 하단 탭바. 트레이너
  인앱(폰) 기능과 데스크탑 관리 기능이 노출 기준에 따라 분기됨
- AI/YOLO: `backend/app/services/`에 OpenAI 요약·리포트·STT(Whisper), YOLO pose
  분석이 **실제로 연동되어 있고**, 키/패키지가 없으면 규칙 기반 fallback으로 항상
  안전하게 동작 (앱이 죽지 않음)
- 시드 데이터: `backend/seed.py` — 트레이너 `trainer1`/`pass1234`, 회원 3명(박수진/이민호/최유나)

## 3. 이번 세션에서 새로 진행한 작업

### 3-1. Daily Schedule (트레이너 일정표)
- DB: `trainer_daily_tasks` 테이블 추가 (`backend/app/schema.sql`, 모든 테이블
  `CREATE TABLE IF NOT EXISTS`라서 기존 DB에도 안전하게 재실행 가능)
- API: `backend/app/routers/tasks.py` (`GET/POST/PUT/DELETE /tasks`, `period=today|week|all`)
- UI: `frontend/components/trainer/daily-schedule.tsx` (Table/Board 뷰 토글, 탭),
  `dashboard-client.tsx` 상단에 삽입됨

### 3-2. Gradio에서 발전시킨 AI/YOLO 코드를 백엔드로 통합 검증
- 루트의 `ai_service.py`/`pose_service.py`(Gradio용, OpenAI 실제 연동 + YOLO 실제
  keypoint 추출)가 이미 `backend/app/services/ai_service.py`, `pose_service.py`,
  `mock_ai.py`로 이식되어 있었음 — 라우터(`sessions.py`, `posture.py`, `reports.py`)에서
  실제로 호출되도록 이미 연결까지 되어 있는 것을 확인
- **Python 3.9 호환성 버그 수정**: 이 서비스 파일들에 `X | None` (PEP604) 문법이
  남아있어서 사용자의 로컬 Python 3.9 환경에서 깨질 수 있었음 → `Optional[X]`로 전부
  교체 (`typing.Optional` import)
- `backend/.env.example` 신규 추가 (`OPENAI_API_KEY`, `OPENAI_MODEL`, `YOLO_POSE_MODEL`,
  이후 `OPENAI_STT_MODEL`도 추가)

### 3-3. Mintlify 기반 디자인 테마 적용
- `getdesign.md`(https://getdesign.md/mintlify/design-md)에서 `npx getdesign@latest add mintlify`로 `frontend/DESIGN.md` 받아옴
- `frontend/app/globals.css`: Tailwind v4 `@theme` 블록에서 **slate/emerald 팔레트
  자체를 재정의**하는 방식으로 적용 (컴포넌트 파일 하나하나 안 고치고 전역 반영).
  민트 accent 토큰(`--color-mint`, `-deep`, `-soft`) 신규 추가
- Inter 폰트 적용 (`next/font/google`, `app/layout.tsx`)
- `components/ui/button.tsx`: 전부 pill(`rounded-full`)로, `accent`(민트) variant 추가
- `components/ui/card.tsx`: `rounded-xl` + hairline 보더, 무거운 그림자 제거
- `components/ui/input.tsx`: 포커스 시 민트 보더/링
- 사이드바 active 메뉴 민트 좌측 인디케이터, 모바일 하단 탭 active 민트색
- 로그인 버튼, Daily Schedule 추가 버튼도 민트 accent로 변경(민트가 안 보인다는
  피드백 받고 눈에 띄는 곳에 추가 적용함)
- **주의**: Tailwind v4는 `tailwind.config.js` 없이 `globals.css`의 `@theme`만 씀.
  색상 커스터마이징은 항상 여기서.

### 3-4. 기능 업그레이드: 카메라 촬영 / 음성 녹음
- **모바일 카메라 촬영**: `session-workspace-client.tsx`의 자세 사진 업로드 input에
  `capture="environment"` 추가(모바일에서 후면 카메라 바로 열림, 데스크탑은 영향 없음).
  업로드 전 로컬 미리보기(blob URL)도 추가
- **음성 녹음(신규 기능)**: 브라우저 `MediaRecorder` API로 마이크 녹음 → 재생/다시
  녹음 → 업로드. `session-workspace-client.tsx`에 "녹음"/"직접 입력" 탭으로 구현
  (기존 텍스트 입력 방식은 fallback으로 유지)
- **백엔드**: `POST /sessions/voice-recording` 신규 엔드포인트(`sessions.py`) —
  오디오 파일을 받아 `backend/app/services/ai_service.py`의 `transcribe_audio()`
  (OpenAI Whisper API)로 텍스트 변환 후, 기존 `summarize_voice_memo()` 재사용해서
  요약까지 한 번에 반환. `OPENAI_API_KEY` 없으면 `transcribed: false` + 안내
  메시지 반환 → 프론트가 자동으로 "직접 입력" 탭으로 전환
  - **STT는 다른 AI 기능과 달리 규칙 기반 fallback이 없음**(대체할 방법이 없어서
    키 필수). 이 부분만 유일하게 "키 없으면 완전히 실패"하는 지점.
- 새 타입: `VoiceRecordingOut`(백엔드 스키마), `VoiceRecordingSummary`(프론트
  `lib/types.ts`)
- 새 아이콘: `MicIcon`, `StopIcon`, `PlayIcon` (`components/ui/icons.tsx`)

### 3-5. 배포 준비 (Railway + Vercel)
- **목적**: 마이크/카메라(`getUserMedia`)는 `localhost` 또는 HTTPS에서만 동작해서,
  실제 폰으로 테스트하려면 HTTPS 배포가 필요함 (로컬 IP `http://192.168.x.x`로는 불가)
- 배포 구조: 백엔드는 Railway(FastAPI + 볼륨으로 SQLite/업로드 파일 영구 저장),
  프론트는 Vercel(Next.js). 레포 분리 안 하고 Root Directory 설정만 다르게 함
- 코드 변경:
  - `backend/app/main.py`: CORS를 `CORS_ORIGINS` 환경변수(콤마 구분)로 읽도록 변경
    (기본값 `http://localhost:3000`)
  - `backend/app/routers/auth.py`: 쿠키에 `COOKIE_SECURE` 환경변수로 Secure 플래그
    켤 수 있게 변경 (기본 False, 배포 시 1)
  - `backend/app/config.py` 신규 — `FITNOTE_UPLOAD_DIR` 환경변수로 업로드 경로를
    영구 볼륨으로 지정 가능하게 함 (`UPLOAD_ROOT`). `main.py`, `posture.py`,
    `sessions.py`가 이걸 공용으로 씀
  - `posture.py`의 `analyze_posture_image`에서 저장된 이미지 경로를 복원하는 로직도
    `UPLOAD_ROOT` 기준으로 수정(이전엔 `BACKEND_DIR` 기준이라 배포 환경에서 깨질 뻔함)
  - `backend/Procfile` 신규 (`web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
- **requirements 분리**: `backend/requirements.txt`에서 무거운 YOLO 관련 패키지
  (`ultralytics`, `opencv-python`, `pillow`, `numpy` — torch 포함이라 빌드 오래 걸림)를
  `backend/requirements-yolo.txt`로 분리. 기본 배포는 가볍게(YOLO는 fallback으로
  동작), 실제 YOLO 테스트하고 싶으면 `pip install -r requirements.txt -r requirements-yolo.txt`
- 배포 가이드: **`DEPLOY.md`**(루트)에 Railway/Vercel 단계별 절차, 환경변수 표,
  폰 테스트 체크리스트 전부 정리되어 있음. 여기부터 시작하면 됨
- **사용자가 직접 Railway/Vercel 가입 + `OPENAI_API_KEY` 입력을 진행하기로 함**
  (API 키는 이 대화에서도 공유된 적 없음). 마지막 대화 시점 기준 배포 진행 여부는
  불확실 — Codex가 이어받으면 사용자에게 진행 상황 먼저 확인할 것

## 4. 남은 작업 / 진행 중인 것

1. **Railway + Vercel 실제 배포** — `DEPLOY.md` 기준으로 사용자가 진행 중이었음.
   완료됐는지, 막힌 부분 있는지 먼저 확인 필요
2. **Claude Design 목업 반영 대기 중** — 사용자가 claude.ai/design에서 디자인
   시스템(Mintlify 기반, `frontend/DESIGN.md` 참고해서 세팅함)을 만들고 화면
   시안을 완성했다고 함. 아직 실제 코드에는 반영 안 됨. "Share → Handoff to Claude
   Code" 기능으로 넘어온 스펙이 있으면 그걸로 반영하면 됨. 사용자에게 어떤 화면
   시안인지, 핸드오프 결과물이 뭔지 먼저 물어볼 것
3. **실제 YOLO 로컬/배포 테스트** — 코드는 완성되어 있지만 무거운 패키지라 아직
   실치 안 함(로컬도, 배포도). 사용자가 필요하다고 하면 `requirements-yolo.txt`
   설치 안내
4. **자동 검증 미완료 항목**: Claude 세션 후반부에 작업 샌드박스가 디스크 부족으로
   막혀서(`ultralytics` 무거운 설치 시도 중 발생, 참고용) `tsc --noEmit`/`py_compile`
   자동 검증을 못 돌렸음. 대신 사용자가 로컬(`uvicorn --reload`)에서 직접 실행해서
   로그인/세션 기록 화면까지 이상 없음을 확인함. 그래도 Codex가 다시 한 번
   `tsc --noEmit`, 백엔드 기동 정도는 확인하고 시작하는 걸 추천

## 5. 아키텍처/컨벤션 (반드시 지킬 것)

- **Python 3.9 호환**: 사용자 로컬 백엔드가 Python 3.9(Xcode 번들 프레임워크)라서
  `X | None` 같은 PEP604 문법 절대 쓰지 말 것. `Optional[X]` (`from typing import Optional`) 사용
- **ORM 없음**: `sqlite3` 직접 사용, Pydantic은 요청/응답 스키마 전용
  (`backend/app/schemas.py`)
- **DB 마이그레이션**: `schema.sql`의 모든 테이블이 `CREATE TABLE IF NOT EXISTS`.
  새 테이블 추가할 때도 이 패턴 유지하면 `init_db()`가 매 startup마다 안전하게 재실행됨
- **인증**: JWT를 httpOnly 쿠키(`access_token`)에 저장. `next.config.ts`의
  rewrites가 `/api/*`, `/uploads/*`를 백엔드로 프록시해서 브라우저 입장에선 항상
  같은 오리진 — 이 구조 덕분에 배포(Vercel+Railway, 서로 다른 도메인)에서도 쿠키가
  깨지지 않음. 서버 컴포넌트는 `lib/server-api.ts`의 `serverGet`이 쿠키를 직접
  읽어서 백엔드에 수동으로 forward함
- **Tailwind v4**: `tailwind.config.js` 없음. 전부 `frontend/app/globals.css`의
  `@theme` 블록에서 관리. 색상 커스터마이징 시 slate/emerald 팔레트를 직접
  재정의하는 방식을 이미 씀 — 새 accent 색이 필요하면 같은 패턴으로 `@theme`에
  `--color-xxx` 추가
- **AI/YOLO 서비스는 항상 fallback 우선**: `backend/app/services/`의 모든 AI
  함수는 예외를 삼키고 규칙 기반 결과나 `None`을 반환하도록 되어 있음(STT 제외).
  새 AI 기능 추가할 때도 이 패턴 유지 — 키/패키지 없어도 앱이 절대 죽으면 안 됨
- **반응형 노출 기준**: 트레이너 화면은 데스크탑 사이드바(전체 메뉴) vs 모바일
  하단 탭바(핵심만). 폰으로 실제 쓰는 기능(사진 촬영, 음성 녹음 등)은 모바일에서
  우선 노출, 관리자스러운 기능(회원 사용량 통계 등)은 데스크탑 위주로 노출하는
  기존 방향 유지

## 6. 로컬 실행

```bash
# 백엔드
cd backend
.venv/bin/pip install -r requirements.txt   # 기본은 가벼운 버전(YOLO 제외)
.venv/bin/python seed.py                     # 최초 1회, 데모 데이터 생성
.venv/bin/python -m uvicorn app.main:app --reload --port 8000

# 프론트엔드 (다른 터미널)
cd frontend
npm install
npm run dev
```

데모 로그인: 트레이너 `trainer1`/`pass1234`, 회원 `박수진`/`5678`

## 7. 참고 문서

- `README.md` — 전체 실행 방법, AI/YOLO 연동 상태
- `DEPLOY.md` — Railway + Vercel 배포 절차 (지금 가장 중요)
- `CLAUDE_HANDOFF.md` — Gradio 프로토타입 단계 기획 문서 (낡음, 참고만)
- `frontend/DESIGN.md` — Mintlify 디자인 시스템 분석 원본 (Claude Design에도 같이 업로드해서 씀)
- `fitnote-trainer-erdcloud-import.sql` — ERD 기준 SQL (실제 `backend/app/schema.sql`과 동기화 확인할 것)

## 8. 시크릿/키 관련

- `OPENAI_API_KEY`는 사용자가 직접 관리함. Claude 세션에서도 절대 공유받은 적
  없고, `.env`/`local_secrets.py`는 `.gitignore`에 포함되어 커밋 안 됨
- Railway/Vercel 계정 정보도 사용자가 직접 가입/설정 중이었음
