# FitNote Trainer - Colab Sample Data & Analysis Queries
#
# 사용법:
# 1. Google Colab 새 노트북을 만든다.
# 2. 이 파일의 코드를 셀에 붙여넣고 위에서부터 실행한다.
# 3. SQLite 메모리 DB에 샘플 데이터가 생성되고, 분석 쿼리 결과가 출력된다.

import sqlite3
import pandas as pd


# -----------------------------------------------------------------------------
# 1. SQLite 연결
# -----------------------------------------------------------------------------

conn = sqlite3.connect(":memory:")
conn.execute("PRAGMA foreign_keys = ON;")


def run_query(sql: str, title: str = ""):
    """SQL 실행 결과를 pandas DataFrame으로 출력한다."""
    if title:
        print(f"\n## {title}")
    return pd.read_sql_query(sql, conn)


# -----------------------------------------------------------------------------
# 2. 테이블 생성
# -----------------------------------------------------------------------------

schema_sql = """
CREATE TABLE trainers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  center_name TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE members (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trainer_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  phone TEXT,
  age INTEGER,
  gender TEXT,
  fitness_goal TEXT,
  exercise_experience TEXT,
  status TEXT DEFAULT 'active',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (trainer_id) REFERENCES trainers(id)
);

CREATE TABLE member_health_notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  pain_area TEXT,
  injury_history TEXT,
  precautions TEXT,
  asymmetry_note TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (member_id) REFERENCES members(id)
);

CREATE TABLE member_body_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  height_cm REAL,
  weight_kg REAL,
  body_type_note TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (member_id) REFERENCES members(id)
);

CREATE TABLE member_consents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  consent_type TEXT NOT NULL,
  consent_text TEXT,
  is_agreed INTEGER DEFAULT 0,
  agreed_at TEXT,
  FOREIGN KEY (member_id) REFERENCES members(id)
);

CREATE TABLE sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  trainer_id INTEGER NOT NULL,
  session_date TEXT NOT NULL,
  focus_area TEXT,
  memo TEXT,
  next_memo TEXT,
  raw_voice_text TEXT,
  summary TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (trainer_id) REFERENCES trainers(id)
);

CREATE TABLE session_exercises (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  exercise_name TEXT NOT NULL,
  sets INTEGER,
  reps INTEGER,
  weight_kg REAL,
  note TEXT,
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE posture_images (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  session_id INTEGER,
  movement_name TEXT,
  image_path TEXT NOT NULL,
  upload_status TEXT DEFAULT 'uploaded',
  uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE posture_analysis (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  posture_image_id INTEGER NOT NULL,
  model_name TEXT,
  movement_name TEXT,
  analysis_status TEXT DEFAULT 'pending',
  main_issue TEXT,
  sub_issue TEXT,
  result_note TEXT,
  analyzed_at TEXT,
  FOREIGN KEY (posture_image_id) REFERENCES posture_images(id)
);

CREATE TABLE posture_keypoints (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  analysis_id INTEGER NOT NULL,
  keypoint_index INTEGER NOT NULL,
  point_name TEXT NOT NULL,
  x REAL,
  y REAL,
  confidence REAL,
  FOREIGN KEY (analysis_id) REFERENCES posture_analysis(id)
);

CREATE TABLE posture_scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  analysis_id INTEGER NOT NULL,
  total_score INTEGER,
  knee_alignment_score INTEGER,
  upper_body_score INTEGER,
  pelvis_balance_score INTEGER,
  lower_body_stability_score INTEGER,
  improvement_points TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (analysis_id) REFERENCES posture_analysis(id)
);

CREATE TABLE feedbacks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  session_id INTEGER,
  analysis_id INTEGER,
  trainer_comment TEXT NOT NULL,
  caution_note TEXT,
  next_check_point TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (session_id) REFERENCES sessions(id),
  FOREIGN KEY (analysis_id) REFERENCES posture_analysis(id)
);

CREATE TABLE assignments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  session_id INTEGER,
  title TEXT NOT NULL,
  description TEXT,
  target_amount TEXT,
  due_date TEXT,
  status TEXT DEFAULT 'unchecked',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  completed_at TEXT,
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE tions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  assignment_id INTEGER NOT NULL,
  checked_at TEXT DEFAULT CURRENT_TIMESTAMP,
  status TEXT DEFAULT 'unchecked',
  note TEXT,
  FOREIGN KEY (assignment_id) REFERENCES assignments(id)
);

CREATE TABLE reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  session_id INTEGER,
  analysis_id INTEGER,
  report_title TEXT,
  workout_summary TEXT,
  posture_summary TEXT,
  good_points TEXT,
  caution_points TEXT,
  next_assignment TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (session_id) REFERENCES sessions(id),
  FOREIGN KEY (analysis_id) REFERENCES posture_analysis(id)
);
"""

conn.executescript(schema_sql)


# -----------------------------------------------------------------------------
# 3. 샘플 데이터 적재
# -----------------------------------------------------------------------------

sample_data_sql = """
INSERT INTO trainers (id, name, email, phone, center_name) VALUES
(1, '김도현', 'dohyun.kim@fitnote.test', '010-1111-2222', '핏노트 PT 센터'),
(2, '이서연', 'seoyeon.lee@fitnote.test', '010-3333-4444', '핏노트 PT 센터');

INSERT INTO members
(id, trainer_id, name, phone, age, gender, fitness_goal, exercise_experience, status)
VALUES
(1, 1, '박민준', '010-1000-0001', 29, 'male', '허리 통증 없이 하체 근력 강화', '헬스 6개월', 'active'),
(2, 1, '최유진', '010-1000-0002', 34, 'female', '체지방 감량과 자세 교정', '필라테스 경험 있음', 'active'),
(3, 1, '정하늘', '010-1000-0003', 41, 'female', '무릎 부담 줄이며 체력 회복', '운동 초보', 'active'),
(4, 2, '강지훈', '010-1000-0004', 26, 'male', '상체 근력 증가', '축구 동호회', 'active');

INSERT INTO member_health_notes
(member_id, pain_area, injury_history, precautions, asymmetry_note)
VALUES
(1, '허리', '요추 염좌 경험', '데드리프트 고중량 금지, 코어 안정화 우선', '오른쪽 골반이 살짝 올라감'),
(2, '목/어깨', '거북목 및 승모근 긴장', '오버헤드 동작 시 목 긴장 확인', '왼쪽 어깨 가동 범위 제한'),
(3, '무릎', '우측 무릎 통증', '스쿼트 깊이 제한, 무릎 안쪽 말림 확인', '오른쪽 무릎 내측 편위'),
(4, NULL, NULL, '고중량 전 충분한 워밍업 필요', NULL);

INSERT INTO member_body_profiles
(member_id, height_cm, weight_kg, body_type_note)
VALUES
(1, 176.5, 72.4, '골반 전방 경사 경향'),
(2, 164.2, 58.1, '상체 말림과 목 긴장 경향'),
(3, 160.8, 63.5, '무릎 안정성 관리 필요'),
(4, 181.0, 78.6, '상체 근력 중심 훈련 적합');

INSERT INTO member_consents
(member_id, consent_type, consent_text, is_agreed, agreed_at)
VALUES
(1, 'body_posture_analysis', '자세 분석 참고용 신체 및 관절 정보 수집 안내', 1, '2026-07-01 10:00:00'),
(2, 'body_posture_analysis', '자세 분석 참고용 신체 및 관절 정보 수집 안내', 1, '2026-07-02 10:30:00'),
(3, 'body_posture_analysis', '자세 분석 참고용 신체 및 관절 정보 수집 안내', 1, '2026-07-03 11:00:00'),
(4, 'body_posture_analysis', '자세 분석 참고용 신체 및 관절 정보 수집 안내', 0, NULL);

INSERT INTO sessions
(id, member_id, trainer_id, session_date, focus_area, memo, next_memo, raw_voice_text, summary)
VALUES
(1, 1, 1, '2026-07-01', '하체/코어', '스쿼트 자세에서 허리 과신전 경향.', '다음 수업에서 힙힌지 재확인.', '민준 회원 스쿼트 3세트, 플랭크 3세트 진행. 허리 과신전 주의.', '하체와 코어 중심 수업. 허리 안정화가 핵심.'),
(2, 1, 1, '2026-07-08', '하체', '지난주보다 스쿼트 안정성 개선.', '런지 동작 추가 예정.', '스쿼트 4세트, 레그프레스 3세트. 무게는 낮게 유지.', '스쿼트 안정성 개선, 하체 근지구력 강화.'),
(3, 2, 1, '2026-07-02', '상체/자세', '목 긴장도가 높음.', '흉추 가동성 스트레칭 과제 확인.', '랫풀다운 3세트, 로우 3세트. 어깨 말림 주의.', '상체 후면 활성화와 자세 교정 중심.'),
(4, 3, 1, '2026-07-03', '하체 재활', '무릎 안쪽 말림 관찰.', '미니밴드 스쿼트 반복.', '박스 스쿼트 3세트, 힙어브덕션 3세트.', '무릎 부담을 낮춘 하체 안정화 수업.'),
(5, 4, 2, '2026-07-04', '상체 근력', '벤치프레스 자세 안정적.', '증량 가능성 확인.', '벤치프레스 4세트, 숄더프레스 3세트.', '상체 근력 강화 수업.');

INSERT INTO session_exercises
(session_id, exercise_name, sets, reps, weight_kg, note)
VALUES
(1, '스쿼트', 3, 10, 30, '허리 과신전 주의'),
(1, '플랭크', 3, 40, NULL, '초 단위 수행'),
(2, '스쿼트', 4, 10, 35, '무릎 정렬 개선'),
(2, '레그프레스', 3, 12, 80, '가동 범위 제한'),
(3, '랫풀다운', 3, 12, 25, '목 긴장 주의'),
(3, '시티드 로우', 3, 12, 20, '견갑 후인 연습'),
(4, '박스 스쿼트', 3, 10, 10, '무릎 안쪽 말림 확인'),
(4, '힙 어브덕션', 3, 15, 15, '둔근 활성화'),
(5, '벤치프레스', 4, 8, 50, '자세 안정적'),
(5, '숄더프레스', 3, 10, 20, '어깨 통증 없음');

INSERT INTO posture_images
(id, member_id, session_id, movement_name, image_path, upload_status, uploaded_at)
VALUES
(1, 1, 1, '스쿼트', '/content/images/member1_squat_0701.jpg', 'analyzed', '2026-07-01 12:20:00'),
(2, 1, 2, '스쿼트', '/content/images/member1_squat_0708.jpg', 'analyzed', '2026-07-08 12:30:00'),
(3, 2, 3, '랫풀다운', '/content/images/member2_latpull_0702.jpg', 'analyzed', '2026-07-02 15:20:00'),
(4, 3, 4, '박스 스쿼트', '/content/images/member3_boxsquat_0703.jpg', 'analyzed', '2026-07-03 16:10:00');

INSERT INTO posture_analysis
(id, posture_image_id, model_name, movement_name, analysis_status, main_issue, sub_issue, result_note, analyzed_at)
VALUES
(1, 1, 'dummy-yolo-v1', '스쿼트', 'success', '허리 과신전', '무릎 안쪽 말림 약간', '코어 브레이싱과 무릎 정렬 피드백 필요.', '2026-07-01 12:25:00'),
(2, 2, 'dummy-yolo-v1', '스쿼트', 'success', '무릎 정렬 개선', '하체 안정성 보통', '이전보다 안정적이나 하단 구간 제어 필요.', '2026-07-08 12:36:00'),
(3, 3, 'dummy-yolo-v1', '랫풀다운', 'success', '어깨 상승', '목 긴장', '견갑 하강 연습 필요.', '2026-07-02 15:25:00'),
(4, 4, 'dummy-yolo-v1', '박스 스쿼트', 'success', '무릎 안쪽 말림', '발 아치 무너짐', '미니밴드와 둔근 활성화 추천.', '2026-07-03 16:15:00');

INSERT INTO posture_keypoints
(analysis_id, keypoint_index, point_name, x, y, confidence)
VALUES
(1, 5, 'left_shoulder', 310.5, 188.2, 0.9821),
(1, 6, 'right_shoulder', 421.7, 190.4, 0.9750),
(1, 11, 'left_hip', 330.1, 360.8, 0.9614),
(1, 12, 'right_hip', 452.3, 365.6, 0.9582),
(1, 13, 'left_knee', 335.1, 510.8, 0.9412),
(1, 14, 'right_knee', 455.3, 515.6, 0.9365),
(1, 15, 'left_ankle', 330.4, 690.2, 0.9120),
(1, 16, 'right_ankle', 462.8, 692.1, 0.9088),
(2, 13, 'left_knee', 338.7, 508.2, 0.9570),
(2, 14, 'right_knee', 450.1, 510.6, 0.9524),
(3, 5, 'left_shoulder', 295.8, 176.3, 0.9440),
(3, 6, 'right_shoulder', 412.4, 180.2, 0.9381),
(4, 13, 'left_knee', 340.0, 520.4, 0.9213),
(4, 14, 'right_knee', 448.6, 528.9, 0.9175);

INSERT INTO posture_scores
(analysis_id, total_score, knee_alignment_score, upper_body_score, pelvis_balance_score, lower_body_stability_score, improvement_points)
VALUES
(1, 68, 62, 70, 66, 72, '코어 브레이싱, 무릎 정렬'),
(2, 78, 76, 80, 75, 82, '하단 구간 제어'),
(3, 72, 80, 60, 76, 74, '목 긴장 완화, 견갑 하강'),
(4, 61, 50, 72, 65, 58, '무릎 정렬, 발 안정성');

INSERT INTO feedbacks
(member_id, session_id, analysis_id, trainer_comment, caution_note, next_check_point)
VALUES
(1, 1, 1, '허리 안정화가 가장 중요합니다. 무게보다 자세를 우선합니다.', '허리 통증 발생 시 즉시 중단', '힙힌지와 복압 확인'),
(1, 2, 2, '지난주보다 스쿼트 안정성이 좋아졌습니다.', '피로 시 무릎이 안쪽으로 들어가지 않게 주의', '런지 동작 도입'),
(2, 3, 3, '등 근육 사용감은 좋지만 목 긴장이 높습니다.', '어깨를 귀에서 멀리 두기', '흉추 가동성'),
(3, 4, 4, '무릎 정렬을 천천히 개선하는 방향이 좋습니다.', '깊은 스쿼트 금지', '미니밴드 스쿼트');

INSERT INTO assignments
(member_id, session_id, title, description, target_amount, due_date, status, completed_at)
VALUES
(1, 1, '데드버그', '허리 안정화를 위한 코어 운동', '하루 3세트 x 10회', '2026-07-07', 'completed', '2026-07-06 21:00:00'),
(1, 2, '힙힌지 연습', '거울 보며 힙힌지 패턴 연습', '하루 5분', '2026-07-14', 'in_progress', NULL),
(2, 3, '흉추 스트레칭', '폼롤러를 활용한 흉추 가동성 운동', '하루 5분', '2026-07-09', 'unchecked', NULL),
(3, 4, '미니밴드 스쿼트', '무릎 정렬을 유지하며 천천히 수행', '주 3회 x 12회', '2026-07-10', 'in_progress', NULL);

INSERT INTO assignment_completions
(assignment_id, checked_at, status, note)
VALUES
(1, '2026-07-03 21:00:00', 'in_progress', '데드버그 2세트 수행'),
(1, '2026-07-06 21:00:00', 'completed', '과제 완료'),
(2, '2026-07-09 20:30:00', 'in_progress', '힙힌지 5분 수행'),
(4, '2026-07-05 19:00:00', 'in_progress', '무릎 통증 없이 수행');

INSERT INTO reports
(member_id, session_id, analysis_id, report_title, workout_summary, posture_summary, good_points, caution_points, next_assignment)
VALUES
(1, 1, 1, '박민준 7월 1일 PT 리포트', '스쿼트와 플랭크 중심 수업.', '허리 과신전과 무릎 정렬 주의.', '코어 운동 집중도가 좋음.', '허리 통증 주의.', '데드버그'),
(1, 2, 2, '박민준 7월 8일 PT 리포트', '스쿼트와 레그프레스 진행.', '스쿼트 안정성 개선.', '지난 수업 대비 점수 향상.', '피로 시 무릎 정렬 주의.', '힙힌지 연습'),
(2, 3, 3, '최유진 7월 2일 PT 리포트', '랫풀다운과 로우 진행.', '어깨 상승과 목 긴장 확인.', '등 운동 수행감 좋음.', '목 긴장 주의.', '흉추 스트레칭'),
(3, 4, 4, '정하늘 7월 3일 PT 리포트', '박스 스쿼트와 힙 어브덕션 진행.', '무릎 안쪽 말림 확인.', '통증 없이 수업 완료.', '깊은 스쿼트 제한.', '미니밴드 스쿼트');
"""

conn.executescript(sample_data_sql)


# -----------------------------------------------------------------------------
# 4. 데이터 확인
# -----------------------------------------------------------------------------

print("테이블 생성 및 샘플 데이터 적재 완료")

table_counts = run_query(
    """
    SELECT 'trainers' AS table_name, COUNT(*) AS row_count FROM trainers
    UNION ALL SELECT 'members', COUNT(*) FROM members
    UNION ALL SELECT 'member_health_notes', COUNT(*) FROM member_health_notes
    UNION ALL SELECT 'member_body_profiles', COUNT(*) FROM member_body_profiles
    UNION ALL SELECT 'member_consents', COUNT(*) FROM member_consents
    UNION ALL SELECT 'sessions', COUNT(*) FROM sessions
    UNION ALL SELECT 'session_exercises', COUNT(*) FROM session_exercises
    UNION ALL SELECT 'posture_images', COUNT(*) FROM posture_images
    UNION ALL SELECT 'posture_analysis', COUNT(*) FROM posture_analysis
    UNION ALL SELECT 'posture_keypoints', COUNT(*) FROM posture_keypoints
    UNION ALL SELECT 'posture_scores', COUNT(*) FROM posture_scores
    UNION ALL SELECT 'feedbacks', COUNT(*) FROM feedbacks
    UNION ALL SELECT 'assignments', COUNT(*) FROM assignments
    UNION ALL SELECT 'assignment_completions', COUNT(*) FROM assignment_completions
    UNION ALL SELECT 'reports', COUNT(*) FROM reports;
    """,
    "테이블별 샘플 데이터 수",
)
display(table_counts)


# -----------------------------------------------------------------------------
# 5. 분석 쿼리 8개
# -----------------------------------------------------------------------------

# Query 1. 회원별 세션 횟수와 최근 수업일
q1 = run_query(
    """
    SELECT
      m.id AS member_id,
      m.name AS member_name,
      t.name AS trainer_name,
      COUNT(s.id) AS session_count,
      MAX(s.session_date) AS last_session_date
    FROM members m
    JOIN trainers t ON m.trainer_id = t.id
    LEFT JOIN sessions s ON m.id = s.member_id
    GROUP BY m.id, m.name, t.name
    ORDER BY session_count DESC, last_session_date DESC;
    """,
    "Query 1. 회원별 세션 횟수와 최근 수업일",
)
display(q1)


# Query 2. 회원별 자세 점수 평균
q2 = run_query(
    """
    SELECT
      m.name AS member_name,
      ROUND(AVG(ps.total_score), 1) AS avg_posture_score,
      MIN(ps.total_score) AS min_score,
      MAX(ps.total_score) AS max_score,
      COUNT(ps.id) AS analysis_count
    FROM members m
    JOIN posture_images pi ON m.id = pi.member_id
    JOIN posture_analysis pa ON pi.id = pa.posture_image_id
    JOIN posture_scores ps ON pa.id = ps.analysis_id
    GROUP BY m.id, m.name
    ORDER BY avg_posture_score DESC;
    """,
    "Query 2. 회원별 자세 점수 평균",
)
display(q2)


# Query 3. 자세 점수가 낮은 분석 결과 TOP 3
q3 = run_query(
    """
    SELECT
      m.name AS member_name,
      pa.movement_name,
      ps.total_score,
      pa.main_issue,
      ps.improvement_points,
      pa.analyzed_at
    FROM posture_scores ps
    JOIN posture_analysis pa ON ps.analysis_id = pa.id
    JOIN posture_images pi ON pa.posture_image_id = pi.id
    JOIN members m ON pi.member_id = m.id
    ORDER BY ps.total_score ASC
    LIMIT 3;
    """,
    "Query 3. 자세 점수가 낮은 분석 결과 TOP 3",
)
display(q3)


# Query 4. 과제 상태별 개수
q4 = run_query(
    """
    SELECT
      status AS assignment_status,
      COUNT(*) AS assignment_count
    FROM assignments
    GROUP BY status
    ORDER BY assignment_count DESC;
    """,
    "Query 4. 과제 상태별 개수",
)
display(q4)


# Query 5. 미완료 과제와 마감일
q5 = run_query(
    """
    SELECT
      m.name AS member_name,
      a.title,
      a.target_amount,
      a.due_date,
      a.status
    FROM assignments a
    JOIN members m ON a.member_id = m.id
    WHERE a.status != 'completed'
    ORDER BY a.due_date ASC;
    """,
    "Query 5. 미완료 과제와 마감일",
)
display(q5)


# Query 6. 회원별 주의사항 + 최근 피드백 요약
q6 = run_query(
    """
    SELECT
      m.name AS member_name,
      h.pain_area,
      h.precautions,
      f.trainer_comment,
      f.next_check_point
    FROM members m
    LEFT JOIN member_health_notes h ON m.id = h.member_id
    LEFT JOIN feedbacks f ON m.id = f.member_id
    WHERE f.id = (
      SELECT MAX(f2.id)
      FROM feedbacks f2
      WHERE f2.member_id = m.id
    )
    OR f.id IS NULL
    ORDER BY m.id;
    """,
    "Query 6. 회원별 주의사항과 최근 피드백",
)
display(q6)


# Query 7. 박민준 회원의 자세 점수 변화
q7 = run_query(
    """
    SELECT
      m.name AS member_name,
      s.session_date,
      pa.movement_name,
      ps.total_score,
      ps.knee_alignment_score,
      ps.upper_body_score,
      ps.pelvis_balance_score,
      ps.lower_body_stability_score
    FROM members m
    JOIN posture_images pi ON m.id = pi.member_id
    JOIN sessions s ON pi.session_id = s.id
    JOIN posture_analysis pa ON pi.id = pa.posture_image_id
    JOIN posture_scores ps ON pa.id = ps.analysis_id
    WHERE m.name = '박민준'
    ORDER BY s.session_date ASC;
    """,
    "Query 7. 특정 회원의 자세 점수 변화",
)
display(q7)


# Query 8. 과제별 수행 체크 이력 요약
q8 = run_query(
    """
    SELECT
      m.name AS member_name,
      a.title AS assignment_title,
      a.status AS current_assignment_status,
      COUNT(ac.id) AS check_count,
      MAX(ac.checked_at) AS last_checked_at,
      COALESCE(
        (
          SELECT ac2.status
          FROM assignment_completions ac2
          WHERE ac2.assignment_id = a.id
          ORDER BY ac2.checked_at DESC
          LIMIT 1
        ),
        'no_check'
      ) AS last_check_status
    FROM assignments a
    JOIN members m ON a.member_id = m.id
    LEFT JOIN assignment_completions ac ON a.id = ac.assignment_id
    GROUP BY a.id, m.name, a.title, a.status
    ORDER BY last_checked_at DESC;
    """,
    "Query 8. 과제별 수행 체크 이력 요약",
)
display(q8)


# -----------------------------------------------------------------------------
# 6. 간단 시각화
# -----------------------------------------------------------------------------

ax = q2.plot(
    kind="bar",
    x="member_name",
    y="avg_posture_score",
    legend=False,
    title="회원별 평균 자세 점수",
    figsize=(8, 4),
)
ax.set_xlabel("회원")
ax.set_ylabel("평균 자세 점수")

ax2 = q4.plot(
    kind="bar",
    x="assignment_status",
    y="assignment_count",
    legend=False,
    title="과제 상태별 개수",
    figsize=(8, 4),
)
ax2.set_xlabel("과제 상태")
ax2.set_ylabel("개수")
