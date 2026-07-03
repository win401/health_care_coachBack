# FitNote Trainer Claude Handoff

이 문서는 Claude에서 실제 웹앱 구현을 시작하기 위한 인수인계 문서입니다. 현재 저장소에는 PRD, ERD SQL, Colab 샘플 데이터/분석 쿼리, Gradio 프로토타입이 준비되어 있습니다.

## 1. 프로젝트 개요

- 제품명: FitNote Trainer
- 목적: 헬스트레이너가 회원별 프로필, 통증/주의사항, 수업 기록, 자세 분석 결과, 피드백, 과제를 관리하고 회원용 리포트를 생성하는 도우미
- 핵심 사용자: PT 트레이너
- MVP 방향: 실제 AI/YOLO/STT 완성보다, 회원 관리부터 수업 기록, 자세 분석 mock, 과제, 리포트까지 이어지는 서비스 흐름을 구현

## 2. 현재 저장소 위치

```txt
/Users/sungwoo/Desktop/work/class/mini_pj/health_care_coachBack
```

GitHub 원격 저장소:

```txt
https://github.com/win401/health_care_coachBack.git
```

현재 브랜치:

```txt
main
```

## 3. 주요 문서/파일

- `README.md`: 프로젝트 개요 및 실행 방법
- `fitnote-trainer-prd.md`: PRD 정리 문서
- `fitnote-trainer-gradio-screen-flow.md`: Gradio 6탭 화면 흐름 정리
- `fitnote-trainer-erd-table-candidates.md`: ERD 테이블 후보 설명
- `fitnote-trainer-erdcloud-import.sql`: ERDCloud import용 CREATE TABLE SQL
- `fitnote-trainer-erdcloud-logical-name-map.csv`: ERDCloud 논리명 매핑표
- `fitnote-trainer-colab-sample-queries.py`: SQLite 샘플 데이터 및 분석 쿼리
- `gradio_app.py`: 현재 Gradio 프로토타입, 6탭 화면 흐름 반영
- `ai_service.py`: OpenAI API 기반 세션 요약/리포트 생성 서비스, API 키가 없으면 fallback
- `pose_service.py`: Ultralytics YOLO pose 기반 자세 분석 서비스, YOLO 사용 불가 시 fallback
- `backend/app/services/ai_service.py`: FastAPI용 OpenAI API 서비스
- `backend/app/services/pose_service.py`: FastAPI용 YOLO pose 서비스
- `backend/app/services/mock_ai.py`: FastAPI에서 AI/YOLO 우선 호출 후 fallback 처리
- `requirements.txt`: Gradio 프로토타입 실행 의존성
- `.env.example`: OpenAI/YOLO/Gradio 실행 환경변수 예시
- `Healthcare_MiniProject_Guide.pdf`: 수업 프로젝트 가이드
- `Create Diagram/`: Figma export 기반 프로세스 다이어그램 Vite 앱

## 4. 현재 Git 상태 주의

아래 파일은 최근 Gradio 대시보드, 6탭 화면 흐름, AI/YOLO optional 연동, FastAPI/Next.js 확장 작업으로 변경되었거나 새로 추가되었습니다.

```txt
M .gitignore
M README.md
M fitnote-trainer-colab-sample-queries.py
M fitnote-trainer-erdcloud-import.sql
M fitnote-trainer-erdcloud-logical-name-map.csv
M fitnote-trainer-gradio-screen-flow.md
?? .env.example
?? ai_service.py
?? backend/
?? frontend/
?? gradio_app.py
?? CLAUDE_HANDOFF.md
?? local_secrets.example.py
?? pose_service.py
?? requirements.txt
```

아직 커밋/푸시하지 않은 상태일 수 있으므로, 실제 작업 시작 전에 `git status`로 확인하세요.

절대 커밋하면 안 되는 파일:

```txt
local_secrets.py
backend/local_secrets.py
.env
*.db
backend/uploads/
yolov8n-pose.pt
*.pt
gradio_server.log
```

위 항목은 `.gitignore`에 포함되어 있어야 합니다. 특히 `local_secrets.py`에는 실제 OpenAI API 키가 들어가므로 GitHub에 올라가면 안 됩니다.

## 5. 확정된 Gradio 화면 구성

실제 웹앱도 이 흐름을 기준으로 구현하면 됩니다.

### Tab 1. 홈 / 회원 대시보드

- 회원 검색/선택
- 미니 달력
- 간단 메모
- 오늘의 수업 확인
- 회원 요약 카드
- 최근 수업 기록
- 최근 자세 분석
- 진행 중 과제
- 오늘 세션에서 할 운동종목 리스트 체크박스
- 체크 후 세션 시작 버튼
- 세션 시작 후 `수업 기록 / 자세 분석 / 과제` 화면으로 이동

### Tab 2. 회원 등록 / 프로필

- 기본 정보 입력
- 운동 목표 입력
- 인바디 프린트 이미지 업로드, 선택 입력
- 정자세 사진 업로드, 선택 입력
- 정자세 사진 YOLO 분석
- 정자세 관절 포인트/스켈레톤 이미지 표시
- 정자세 관절 좌표 테이블 수정
- 수정 좌표 기준 스켈레톤 다시 그리기
- 가동성 체크 자유 텍스트
- 비대칭 유무: 어깨, 골반, 기타 입력
- 통증/주의사항 입력
- 정보 수집 안내 동의
- 회원 저장

### Tab 3. 수업 기록 / 자세 분석 / 과제

- 회원 및 수업 정보 선택
- 세션 기록 작성
- 텍스트 기반 음성 메모 요약
- 자세 사진 업로드 및 분석
- 트레이너 피드백 작성
- 과제 등록
- 전체 저장

### Tab 4. 회원 리포트

- 회원/세션 선택
- 오늘의 운동 요약
- 자세 분석 결과
- 트레이너 피드백
- 다음 과제
- 리포트 생성

### Tab 5. 회원 전용 화면

- 회원 프로필
- 과제 확인
- 일정 확인
- 변화기록 history 확인
- 운동 자세별 점수 변화 테이블
- 몸무게 변화 테이블
- 달력: 한달 출석률, 남은 세션, PT 예약 확인

### Tab 6. 서비스 관리자

- 전체 KPI: 트레이너 수, 회원 수, 누적 수업 수, 자세 분석 수, 리포트 수, 과제 완료율
- 트레이너별 사용량: 담당 회원 수, 수업 기록 수, 자세 분석 수, 과제 부여 수, 리포트 생성 수
- 회원별 사용량: 누적 수업 수, 자세 분석 수, 과제 수, 과제 완료율, 리포트 수, 최근 이용일
- 날짜별 서비스 활성도: 수업 기록 수, 자세 분석 수, 리포트 생성 수
- 운동종목 기록 빈도
- 과제 완료/마감 관리
- 낮은 자세 점수 및 개선 포인트

## 6. 현재 Gradio 프로토타입 상태

실행 방법:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python gradio_app.py
```

로컬 주소:

```txt
http://127.0.0.1:7860
```

현재 `gradio_app.py`는 기본 실행 시 로컬 전용으로 실행됩니다.

```python
share=os.getenv("GRADIO_SHARE") == "1"
```

따라서 일반 실행은 로컬 서버만 열립니다.

```bash
.venv/bin/python gradio_app.py
```

공개 링크가 필요할 때만 아래처럼 실행합니다.

```bash
GRADIO_SHARE=1 .venv/bin/python gradio_app.py
```

Gradio 공개 링크는 `https://...gradio.live` 형태이며, 로컬 서버가 꺼지면 같이 끊기고 72시간 후 만료됩니다. 현재는 로컬 개발 편의를 위해 공개 링크보다 `http://127.0.0.1:7860` 사용을 우선합니다.

현재 마지막 확인 기준 로컬 서버는 아래 주소로 실행했습니다.

```txt
http://127.0.0.1:7860
```

중요 의존성:

```txt
gradio>=4.44.0
huggingface_hub<1.0
pandas>=2.0.0
pydantic<2.11
openai>=1.0.0
ultralytics>=8.0.0
opencv-python>=4.8.0
pillow>=10.0.0
numpy>=1.24.0
```

`pydantic<2.11`은 Gradio 4.44.1에서 API 스키마 오류를 피하기 위해 고정했습니다.

AI/YOLO 환경변수:

```bash
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
YOLO_POSE_MODEL=yolov8n-pose.pt
GRADIO_SHARE=0
```

사용자가 코드 파일에 직접 키를 넣고 싶다면 아래 방식도 지원합니다.

```bash
cp local_secrets.example.py local_secrets.py
```

`local_secrets.py`:

```python
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4o-mini"
```

`local_secrets.py`와 `backend/local_secrets.py`는 `.gitignore`에 포함되어 있어 GitHub에 커밋되지 않습니다. Gradio의 `ai_service.py`와 FastAPI의 `backend/app/services/ai_service.py` 모두 프로젝트 루트의 `local_secrets.py`를 읽습니다.

`OPENAI_API_KEY`가 없거나 `openai` 패키지가 없으면 세션 요약과 리포트 생성은 기존 규칙 기반 fallback으로 동작합니다. `ultralytics` 설치 또는 YOLO 모델 로딩이 실패하면 자세 분석도 fallback keypoint/점수로 저장되어 발표 중 앱이 중단되지 않습니다.

## 6-1. 지금까지 실제 반영된 Gradio 업데이트

`gradio_app.py`에 다음 기능을 반영했습니다.

### 홈 / 회원 대시보드

- 미니 달력 HTML 렌더링
- 오늘의 수업 목록 표시
- 간단 메모 입력
- 선택 회원 요약 카드
- 최근 수업 기록
- 최근 자세 분석
- 진행 중 과제
- 오늘 세션에서 할 운동종목 체크박스
- `체크 후 세션 시작` 버튼
- 버튼 클릭 시 `수업 기록 / 자세 분석 / 과제` 탭으로 이동
- 선택 운동종목과 메모를 세션 기록 입력값으로 전달

### 회원 등록 / 프로필

- 인바디 프린트 이미지 업로드, 선택 입력
- 정자세 사진 업로드, 선택 입력
- 가동성 체크 자유 텍스트
- 어깨 비대칭 체크
- 골반 비대칭 체크
- 기타 비대칭 입력
- 인바디/가동성 정보는 현재 MVP에서는 `member_body_profiles.body_type_note`에 요약 저장
- 정자세 사진은 현재 MVP에서는 `posture_images`에 `정자세 프로필`로 저장
- 비대칭 정보는 현재 MVP에서는 `member_health_notes.asymmetry_note`에 저장

### 회원 전용 화면

- `Tab 5. 회원 전용 화면` 추가
- 회원 프로필 카드
- 과제 확인 테이블
- 일정 확인 테이블
- 변화기록 history 테이블
- 운동 자세별 점수 변화 테이블
- 몸무게 변화 테이블
- 달력/출석률/남은 세션/PT 예약 요약 카드
- 출석/예약 기록 테이블

### 서비스 관리자

- `Tab 6. 서비스 관리자` 추가
- 전체 서비스 KPI 카드
- 트레이너별 사용량 테이블
- 회원별 사용량 테이블
- 날짜별 서비스 활성도 테이블
- 운동종목 기록 빈도 테이블
- 과제 완료/마감 관리 테이블
- 낮은 자세 점수 및 개선 포인트 테이블
- 관리자 데이터 새로고침 버튼

### AI API / YOLO pose 연동

- `ai_service.py` 추가
- `summarize_voice()`가 OpenAI API 요약을 우선 사용하고, 실패하면 규칙 기반 요약 사용
- `generate_report()`가 OpenAI API JSON 리포트 생성을 우선 사용하고, 실패하면 기존 템플릿 리포트 사용
- Gradio 화면에 `AI 분석 상태` 표시 추가: OpenAI API 사용/fallback 사용 여부 확인 가능
- `local_secrets.py` 기반 키 입력 지원 추가: 사용자가 직접 코드 파일에 API 키를 넣어도 GitHub에는 올라가지 않음
- FastAPI 백엔드도 동일한 키 설정을 읽어서 `/sessions/voice-summary`, `/reports`에서 OpenAI API 사용 가능
- `pose_service.py` 추가
- `save_training_flow()`에서 자세 이미지가 있으면 YOLO pose 분석을 우선 수행
- YOLO 추론 결과는 `posture_analysis`, `posture_keypoints`, `posture_scores`에 저장
- YOLO 사용 불가 시 fallback keypoint와 점수를 저장
- YOLO 관절 포인트/스켈레톤 이미지 렌더링 추가
- Tab 3 수업 기록에서 자세 사진 업로드 후 `전체 저장` 시 스켈레톤 결과 이미지 표시
- Tab 2 회원 등록에서 정자세 사진 업로드 후 YOLO 분석 및 좌표 보정 가능
- 좌표 보정은 현재 Gradio MVP 기준으로 이미지 드래그가 아니라 `x`, `y`, `confidence` 숫자 테이블 수정 후 다시 그리는 방식

### 실행 안정화

- 기본 실행은 로컬 전용
- 공개 링크는 `GRADIO_SHARE=1`일 때만 생성
- `gradio_server.log`는 `.gitignore`에 추가
- `GRADIO_SERVER_PORT`를 `demo.launch(server_port=...)`에 직접 전달하도록 수정
- 기본 포트 탐색 실패 시 빈 포트를 직접 지정해 실행 가능

최근 검증:

```txt
syntax ok
import ok
OpenAI key loaded: Gradio/FastAPI both true
YOLO pose real test: ultralytics:yolov8n-pose.pt success 17 keypoints
YOLO non-person image: fallback 처리 확인
Gradio public share link: GRADIO_SHARE=1 + GRADIO_SERVER_PORT 지정으로 실행 확인
```

## 7. 현재 AI/YOLO/STT 적용 상태

Gradio 프로토타입에는 실제 AI API와 YOLO pose를 붙일 수 있는 서비스 계층을 추가했습니다.

현재 상태:

- 세션 메모 요약: `OPENAI_API_KEY`가 있으면 OpenAI API 사용, 없으면 규칙 기반 fallback
- 회원 리포트 생성: `OPENAI_API_KEY`가 있으면 OpenAI API로 JSON 리포트 문장 생성, 없으면 템플릿 fallback
- 키 설정 방식: 환경변수, `.env`, 프로젝트 루트 `local_secrets.py` 지원
- AI 상태 표시: Gradio에서 `OpenAI API 사용됨` 또는 `fallback 사용됨` 표시
- 자세 분석: `ultralytics`와 YOLO pose 모델을 사용할 수 있으면 keypoint 추출, 실패하면 fallback keypoint/점수 저장
- 자세 시각화: keypoint와 COCO skeleton을 원본 이미지 위에 그린 PNG 생성
- 정자세 보정: 회원 등록 탭에서 YOLO 추출 keypoint 좌표를 DataFrame으로 수정하고 다시 렌더링 가능
- 사진 업로드: `posture_images`, `posture_analysis`, `posture_keypoints`, `posture_scores` 저장 흐름 연결
- STT: 실제 음성 녹음/STT는 아직 미적용, 텍스트 입력 기반 요약만 구현

발표 시 표현:

```txt
현재 Gradio 프로토타입은 OpenAI API와 YOLO pose 연동 구조를 포함하며,
API 키나 모델 환경이 없을 때도 fallback으로 안정적으로 동작합니다.
단, 실제 음성 녹음/STT는 이번 MVP 범위에서 제외했습니다.
```

## 8. ERD 핵심 테이블

현재 SQL 기준 주요 테이블은 다음과 같습니다.

- `trainers`: 트레이너
- `members`: 회원 기본 정보
- `member_health_notes`: 통증, 부상, 주의사항
- `member_body_profiles`: 키, 체중, 신체 특성
- `member_consents`: 개인정보/건강정보 수집 동의
- `sessions`: PT 수업 기록
- `session_exercises`: 세션별 운동 종목
- `posture_images`: 자세 분석용 이미지
- `posture_analysis`: 자세 분석 결과
- `posture_keypoints`: YOLO pose keypoint 좌표
- `posture_scores`: 자세 점수
- `feedbacks`: 트레이너 피드백
- `assignments`: 회원 과제
- `assignment_completions`: 과제 수행 체크 이력
- `reports`: 회원 리포트

ERDCloud에는 `fitnote-trainer-erdcloud-import.sql`을 기준으로 반영하면 됩니다.

## 9. YOLO 적용 설계

현재 Gradio 프로토타입의 YOLO pose 처리 흐름:

1. 자세 사진 업로드
2. `ultralytics` 패키지 설치 여부 확인
3. `YOLO_POSE_MODEL` 환경변수 또는 기본 `yolov8n-pose.pt` 모델 로드
4. 이미지에서 keypoint 추출
5. `posture_keypoints`에 `keypoint_index`, `point_name`, `x`, `y`, `confidence` 저장
6. 주요 관절 좌표로 간단 점수 계산
7. `posture_analysis`, `posture_scores`에 분석 결과 저장

YOLO pose keypoint index는 일반적으로 COCO 17 keypoint 기준을 따릅니다. `posture_keypoints.keypoint_index`는 이 번호를 저장하기 위해 추가한 컬럼입니다.

## 10. 실제 웹앱 구현 권장 방향

이 저장소의 상위 `AGENTS.md` 기준은 `Python-first, Next.js-frontend`입니다.

권장 구조:

```txt
backend/
  app/
    main.py
    database.py
    models.py
    schemas.py
    routers/
      members.py
      sessions.py
      posture.py
      assignments.py
      reports.py
  requirements.txt

frontend/
  app/
  components/
  lib/
  package.json
```

권장 기술:

- Backend: FastAPI
- DB: 초기에는 SQLite, 이후 필요 시 PostgreSQL 전환 가능
- Frontend: Next.js
- UI: shadcn/ui 또는 기본 Tailwind
- AI/YOLO: Gradio와 FastAPI backend 모두 optional 실제 연동 구조가 있으며, API 키/모델이 없으면 fallback 사용

## 11. 우선 구현 순서

1. `fitnote-trainer-erdcloud-import.sql` 기준으로 SQLite DB 초기화
2. FastAPI backend 생성
3. 회원 CRUD API 구현
4. 회원 등록 시 인바디 이미지, 정자세 사진, 가동성 체크, 비대칭 메모 저장 구조 구현
5. 홈 대시보드의 미니 달력, 오늘 수업, 운동 체크 후 세션 시작 흐름 구현
6. 세션 기록 API 구현
7. 과제 등록/조회 API 구현
8. 자세 분석 mock API 구현
9. 리포트 생성 API 구현
10. 회원 전용 화면 API 및 그래프 데이터 구현
11. Next.js에서 6개 화면 흐름 구현
12. 샘플 데이터 seed 스크립트 추가
13. README 실행 방법 업데이트

## 12. MVP에서 반드시 보여줘야 하는 데모 시나리오

1. 신규 회원 등록
2. 운동 목표와 통증/주의사항 저장
3. 홈 대시보드에서 회원 요약 확인
4. 미니 달력에서 오늘 수업과 메모 확인
5. 오늘 진행할 운동종목 체크 후 세션 시작
6. 수업 기록 작성
7. 음성 메모 텍스트를 요약
8. 자세 사진 업로드 후 YOLO pose 또는 fallback 분석 결과 표시
9. 트레이너 피드백 작성
10. 과제 등록
11. 회원 리포트 생성
12. 회원 전용 화면에서 과제, 일정, 변화 기록, 출석 달력 확인
13. 서비스 관리자 화면에서 트레이너/회원 사용량 확인

## 13. 주의 사항

- Gradio는 실제 AI/Yolo optional 연동 구조가 있지만, API 키/모델이 없으면 fallback으로 동작한다는 점을 명확히 할 것
- FastAPI/Next.js 실제 웹앱 쪽도 optional AI/YOLO 서비스 계층은 추가되어 있으나, 실행 환경에 API 키/YOLO 모델이 없으면 fallback 결과가 나온다는 점을 설명할 것
- `node_modules`, `.next`, `.venv`, `.env`는 커밋하지 말 것
- 기존 문서와 SQL 파일을 임의로 삭제하지 말 것
- ERD와 실제 테이블명이 어긋나지 않도록 `fitnote-trainer-erdcloud-import.sql`을 기준으로 맞출 것
- `assignment_completions` 테이블은 과제 상태 변경 이력을 저장하는 용도이며, 실제 UI에서는 우선 `assignments.status`만 써도 됨

## 14. 바로 확인할 명령어

```bash
git status --short
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python gradio_app.py
```

## 15. 다음 Claude 작업 요청 예시

```txt
이 저장소의 CLAUDE_HANDOFF.md를 기준으로 FastAPI backend와 Next.js frontend 구조를 만들고,
Gradio 6탭 흐름을 실제 웹앱 화면으로 구현해줘.
우선 SQLite 기반으로 회원 등록, 홈 대시보드, 수업 기록, 자세 분석, 과제 등록, 리포트 생성, 회원 전용 화면, 서비스 관리자 화면까지 동작하게 해줘.
```
