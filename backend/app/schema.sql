-- FitNote Trainer SQLite schema
-- 이 파일은 상위 fitnote-trainer-erdcloud-import.sql(ERD 기준 문서)을 SQLite 런타임에 맞게
-- 변환한 것입니다. 테이블/컬럼 구성을 바꿀 때는 두 파일을 함께 맞춰주세요.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS trainers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  center_name TEXT,
  login_id TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS members (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trainer_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  phone TEXT,
  age INTEGER,
  gender TEXT,
  fitness_goal TEXT,
  exercise_experience TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (trainer_id) REFERENCES trainers(id)
);

CREATE TABLE IF NOT EXISTS member_health_notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  pain_area TEXT,
  injury_history TEXT,
  precautions TEXT,
  asymmetry_note TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (member_id) REFERENCES members(id)
);

CREATE TABLE IF NOT EXISTS member_body_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  height_cm REAL,
  weight_kg REAL,
  body_type_note TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (member_id) REFERENCES members(id)
);

CREATE TABLE IF NOT EXISTS member_consents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  consent_type TEXT NOT NULL,
  consent_text TEXT,
  is_agreed INTEGER NOT NULL DEFAULT 0,
  agreed_at TEXT,
  FOREIGN KEY (member_id) REFERENCES members(id)
);

CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  trainer_id INTEGER NOT NULL,
  session_date TEXT NOT NULL,
  focus_area TEXT,
  memo TEXT,
  next_memo TEXT,
  raw_voice_text TEXT,
  summary TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (trainer_id) REFERENCES trainers(id)
);

CREATE TABLE IF NOT EXISTS session_exercises (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  exercise_name TEXT NOT NULL,
  sets INTEGER,
  reps INTEGER,
  weight_kg REAL,
  note TEXT,
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS posture_images (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  session_id INTEGER,
  movement_name TEXT,
  image_path TEXT NOT NULL,
  upload_status TEXT NOT NULL DEFAULT 'uploaded',
  uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS posture_analysis (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  posture_image_id INTEGER NOT NULL,
  model_name TEXT,
  movement_name TEXT,
  analysis_status TEXT NOT NULL DEFAULT 'pending',
  main_issue TEXT,
  sub_issue TEXT,
  result_note TEXT,
  analyzed_at TEXT,
  FOREIGN KEY (posture_image_id) REFERENCES posture_images(id)
);

CREATE TABLE IF NOT EXISTS posture_keypoints (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  analysis_id INTEGER NOT NULL,
  keypoint_index INTEGER NOT NULL,
  point_name TEXT NOT NULL,
  x REAL,
  y REAL,
  confidence REAL,
  FOREIGN KEY (analysis_id) REFERENCES posture_analysis(id)
);

CREATE TABLE IF NOT EXISTS posture_scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  analysis_id INTEGER NOT NULL,
  total_score INTEGER,
  knee_alignment_score INTEGER,
  upper_body_score INTEGER,
  pelvis_balance_score INTEGER,
  lower_body_stability_score INTEGER,
  improvement_points TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (analysis_id) REFERENCES posture_analysis(id)
);

CREATE TABLE IF NOT EXISTS feedbacks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  session_id INTEGER,
  analysis_id INTEGER,
  trainer_comment TEXT NOT NULL,
  caution_note TEXT,
  next_check_point TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (session_id) REFERENCES sessions(id),
  FOREIGN KEY (analysis_id) REFERENCES posture_analysis(id)
);

CREATE TABLE IF NOT EXISTS assignments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  session_id INTEGER,
  title TEXT NOT NULL,
  description TEXT,
  target_amount TEXT,
  due_date TEXT,
  status TEXT NOT NULL DEFAULT 'unchecked',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  completed_at TEXT,
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS assignment_completions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  assignment_id INTEGER NOT NULL,
  checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status TEXT NOT NULL DEFAULT 'unchecked',
  note TEXT,
  FOREIGN KEY (assignment_id) REFERENCES assignments(id)
);

CREATE TABLE IF NOT EXISTS reports (
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
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (session_id) REFERENCES sessions(id),
  FOREIGN KEY (analysis_id) REFERENCES posture_analysis(id)
);

CREATE TABLE IF NOT EXISTS trainer_daily_tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trainer_id INTEGER NOT NULL,
  task_date TEXT NOT NULL,
  time_label TEXT,
  title TEXT NOT NULL,
  notes TEXT,
  is_done INTEGER NOT NULL DEFAULT 0,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (trainer_id) REFERENCES trainers(id)
);
