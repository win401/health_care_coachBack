# FitNote Trainer 배포 가이드 (Railway + Vercel)

목표: 실제 폰(모바일 브라우저)에서 카메라 촬영/마이크 녹음까지 테스트할 수 있도록
HTTPS로 배포한다. 브라우저의 `getUserMedia`(카메라/마이크)는 `localhost` 또는
HTTPS에서만 동작하기 때문에, 로컬 IP(`http://192.168.x.x:3000`)로는 마이크/카메라
권한이 막힌다. 그래서 백엔드/프론트엔드를 각각 HTTPS 도메인으로 배포한다.

- 백엔드(FastAPI + SQLite) → Railway
- 프론트엔드(Next.js) → Vercel

두 서비스 다 GitHub 레포(`win401/health_care_coachBack`)를 그대로 연결해서 배포한다.
레포를 나눌 필요는 없고, 각 플랫폼에서 "Root Directory"만 다르게 지정하면 된다.

## 0. 배포 전 체크

- [x] CORS: `backend/app/main.py`가 `CORS_ORIGINS` 환경변수로 허용 도메인을 읽도록 수정됨
- [x] 쿠키: `backend/app/routers/auth.py`가 `COOKIE_SECURE` 환경변수로 Secure 플래그를 켤 수 있도록 수정됨
- [x] DB/업로드 경로: `FITNOTE_DB_PATH`, `FITNOTE_UPLOAD_DIR` 환경변수로 영구 볼륨 경로를 지정할 수 있도록 수정됨
- [x] `backend/Procfile` 추가됨 (`web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`)

## 1. 백엔드 배포 (Railway)

1. [railway.app](https://railway.app) 에서 GitHub 계정으로 가입 (신용카드 불필요, $5 크레딧 30일 무료 체험)
2. New Project → Deploy from GitHub repo → `win401/health_care_coachBack` 선택
3. 서비스 설정에서:
   - **Root Directory**: `backend`
   - **Start Command**: 자동으로 `Procfile`을 인식하지 못하면 `uvicorn app.main:app --host 0.0.0.0 --port $PORT` 직접 입력
4. **Volume 추가** (SQLite/업로드 파일을 재배포 후에도 유지하기 위해 필수)
   - 서비스 → Settings → Volumes → New Volume
   - Mount Path: `/data`
5. **환경변수 설정** (서비스 → Variables)

   ```
   FITNOTE_DB_PATH=/data/fitnote_trainer.db
   FITNOTE_UPLOAD_DIR=/data/uploads
   COOKIE_SECURE=1
   CORS_ORIGINS=https://<나중에 정할 vercel 도메인>.vercel.app
   OPENAI_API_KEY=<본인 키, 여기서 직접 입력>
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_STT_MODEL=whisper-1
   ```

   `CORS_ORIGINS`는 3단계에서 Vercel 도메인이 나온 뒤에 다시 채워도 됩니다(먼저 배포 →
   나중에 값 채워서 재배포).

6. **무거운 AI 패키지는 기본 제외됨** — `ultralytics`/`opencv-python`/`numpy`(실제
   YOLO용, torch 포함이라 무거움)는 `backend/requirements-yolo.txt`로 분리해뒀고,
   Railway는 기본적으로 `backend/requirements.txt`만 설치하므로 지금은 가볍게
   배포됩니다. 자세 분석은 자동으로 fallback으로 동작하니 에러는 안 납니다.
   나중에 실제 YOLO 분석까지 테스트하고 싶으면 Claude한테 다시 요청하면 됩니다 —
   Railway의 빌드 커맨드를 `pip install -r requirements.txt -r requirements-yolo.txt`로
   바꾸고 재배포하는 식으로 켤 수 있습니다.

7. 배포되면 Railway가 `https://xxxx.up.railway.app` 형태의 URL을 줍니다. 이걸
   프론트엔드 배포 때 `BACKEND_ORIGIN`으로 씁니다.

8. **시드 데이터 생성** (데모 로그인 계정 만들기) — Railway 대시보드의 서비스 →
   "Shell" 또는 Railway CLI(`railway run`)로 1회 실행:

   ```bash
   python seed.py
   ```

   실행 안 하면 트레이너 로그인 계정이 없는 빈 DB로 시작합니다.

## 2. 프론트엔드 배포 (Vercel)

1. [vercel.com](https://vercel.com) 에서 GitHub 계정으로 가입
2. New Project → 같은 레포(`win401/health_care_coachBack`) import
3. 프로젝트 설정에서:
   - **Root Directory**: `frontend`
   - Framework Preset: Next.js (자동 인식됨)
4. **환경변수 설정** (Project Settings → Environment Variables)

   ```
   BACKEND_ORIGIN=https://xxxx.up.railway.app   (1단계 7번에서 받은 Railway URL)
   ```

5. Deploy. 완료되면 `https://<프로젝트명>.vercel.app` 형태의 HTTPS URL이 생깁니다.
   이 주소가 폰에서 접속할 최종 URL입니다.

6. Railway로 돌아가서 `CORS_ORIGINS`에 방금 나온 Vercel 도메인을 채워넣고
   재배포합니다.

   ```
   CORS_ORIGINS=https://<프로젝트명>.vercel.app
   ```

## 3. 폰에서 테스트

1. 폰 브라우저(사파리/크롬)로 `https://<프로젝트명>.vercel.app/login` 접속
2. 트레이너 로그인: `trainer1` / `pass1234` (seed.py 실행했을 경우)
3. 회원 세션 기록 화면 → 자세 사진 "촬영" 버튼 → 카메라 권한 허용 → 후면 카메라로 촬영
4. 음성 메모 → "녹음" 탭 → 마이크 권한 허용 → 녹음/정지/재생 확인 → "업로드 후 요약"

HTTPS 도메인이라 `getUserMedia` 권한 요청이 정상적으로 뜹니다. localhost/IP 직접
접속과 달리 여기서 막히면 배포 설정(도메인 자체가 HTTP인지, 리버스 프록시가
깨졌는지) 문제일 가능성이 높습니다.

## 참고: 환경변수 요약

| 위치 | 변수 | 용도 |
|---|---|---|
| Railway (backend) | `FITNOTE_DB_PATH` | SQLite 파일을 볼륨 경로에 고정 |
| Railway (backend) | `FITNOTE_UPLOAD_DIR` | 업로드 사진/음성 파일을 볼륨 경로에 고정 |
| Railway (backend) | `COOKIE_SECURE` | HTTPS 배포에서 `1`로 설정 |
| Railway (backend) | `CORS_ORIGINS` | Vercel 도메인 허용 |
| Railway (backend) | `OPENAI_API_KEY` 등 | AI 기능 (본인이 직접 입력) |
| Vercel (frontend) | `BACKEND_ORIGIN` | Railway 백엔드 URL |
