CREATE TABLE trainers (
  id BIGINT NOT NULL AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  email VARCHAR(100),
  phone VARCHAR(30),
  center_name VARCHAR(100),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE members (
  id BIGINT NOT NULL AUTO_INCREMENT,
  trainer_id BIGINT NOT NULL,
  name VARCHAR(50) NOT NULL,
  phone VARCHAR(30),
  age INT,
  gender VARCHAR(20),
  fitness_goal VARCHAR(255),
  exercise_experience TEXT,
  status VARCHAR(30) NOT NULL DEFAULT 'active',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_members_trainer
    FOREIGN KEY (trainer_id) REFERENCES trainers (id)
);

CREATE TABLE member_health_notes (
  id BIGINT NOT NULL AUTO_INCREMENT,
  member_id BIGINT NOT NULL,
  pain_area VARCHAR(100),
  injury_history TEXT,
  precautions TEXT,
  asymmetry_note TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_member_health_notes_member
    FOREIGN KEY (member_id) REFERENCES members (id)
);

CREATE TABLE member_body_profiles (
  id BIGINT NOT NULL AUTO_INCREMENT,
  member_id BIGINT NOT NULL,
  height_cm DECIMAL(5,2),
  weight_kg DECIMAL(5,2),
  body_type_note TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_member_body_profiles_member
    FOREIGN KEY (member_id) REFERENCES members (id)
);

CREATE TABLE member_consents (
  id BIGINT NOT NULL AUTO_INCREMENT,
  member_id BIGINT NOT NULL,
  consent_type VARCHAR(50) NOT NULL,
  consent_text TEXT,
  is_agreed BOOLEAN NOT NULL DEFAULT FALSE,
  agreed_at DATETIME,
  PRIMARY KEY (id),
  CONSTRAINT fk_member_consents_member
    FOREIGN KEY (member_id) REFERENCES members (id)
);

CREATE TABLE sessions (
  id BIGINT NOT NULL AUTO_INCREMENT,
  member_id BIGINT NOT NULL,
  trainer_id BIGINT NOT NULL,
  session_date DATE NOT NULL,
  focus_area VARCHAR(100),
  memo TEXT,
  next_memo TEXT,
  raw_voice_text TEXT,
  summary TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_sessions_member
    FOREIGN KEY (member_id) REFERENCES members (id),
  CONSTRAINT fk_sessions_trainer
    FOREIGN KEY (trainer_id) REFERENCES trainers (id)
);

CREATE TABLE session_exercises (
  id BIGINT NOT NULL AUTO_INCREMENT,
  session_id BIGINT NOT NULL,
  exercise_name VARCHAR(100) NOT NULL,
  sets INT,
  reps INT,
  weight_kg DECIMAL(6,2),
  note TEXT,
  PRIMARY KEY (id),
  CONSTRAINT fk_session_exercises_session
    FOREIGN KEY (session_id) REFERENCES sessions (id)
);

CREATE TABLE posture_images (
  id BIGINT NOT NULL AUTO_INCREMENT,
  member_id BIGINT NOT NULL,
  session_id BIGINT,
  movement_name VARCHAR(100),
  image_path VARCHAR(500) NOT NULL,
  upload_status VARCHAR(30) NOT NULL DEFAULT 'uploaded',
  uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_posture_images_member
    FOREIGN KEY (member_id) REFERENCES members (id),
  CONSTRAINT fk_posture_images_session
    FOREIGN KEY (session_id) REFERENCES sessions (id)
);

CREATE TABLE posture_analysis (
  id BIGINT NOT NULL AUTO_INCREMENT,
  posture_image_id BIGINT NOT NULL,
  model_name VARCHAR(100),
  movement_name VARCHAR(100),
  analysis_status VARCHAR(30) NOT NULL DEFAULT 'pending',
  main_issue VARCHAR(255),
  sub_issue VARCHAR(255),
  result_note TEXT,
  analyzed_at DATETIME,
  PRIMARY KEY (id),
  CONSTRAINT fk_posture_analysis_image
    FOREIGN KEY (posture_image_id) REFERENCES posture_images (id)
);

CREATE TABLE posture_keypoints (
  id BIGINT NOT NULL AUTO_INCREMENT,
  analysis_id BIGINT NOT NULL,
  keypoint_index INT NOT NULL,
  point_name VARCHAR(50) NOT NULL,
  x DECIMAL(8,3),
  y DECIMAL(8,3),
  confidence DECIMAL(5,4),
  PRIMARY KEY (id),
  CONSTRAINT fk_posture_keypoints_analysis
    FOREIGN KEY (analysis_id) REFERENCES posture_analysis (id)
);

CREATE TABLE posture_scores (
  id BIGINT NOT NULL AUTO_INCREMENT,
  analysis_id BIGINT NOT NULL,
  total_score INT,
  knee_alignment_score INT,
  upper_body_score INT,
  pelvis_balance_score INT,
  lower_body_stability_score INT,
  improvement_points TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_posture_scores_analysis
    FOREIGN KEY (analysis_id) REFERENCES posture_analysis (id)
);

CREATE TABLE feedbacks (
  id BIGINT NOT NULL AUTO_INCREMENT,
  member_id BIGINT NOT NULL,
  session_id BIGINT,
  analysis_id BIGINT,
  trainer_comment TEXT NOT NULL,
  caution_note TEXT,
  next_check_point TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_feedbacks_member
    FOREIGN KEY (member_id) REFERENCES members (id),
  CONSTRAINT fk_feedbacks_session
    FOREIGN KEY (session_id) REFERENCES sessions (id),
  CONSTRAINT fk_feedbacks_analysis
    FOREIGN KEY (analysis_id) REFERENCES posture_analysis (id)
);

CREATE TABLE assignments (
  id BIGINT NOT NULL AUTO_INCREMENT,
  member_id BIGINT NOT NULL,
  session_id BIGINT,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  target_amount VARCHAR(100),
  due_date DATE,
  status VARCHAR(30) NOT NULL DEFAULT 'unchecked',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME,
  PRIMARY KEY (id),
  CONSTRAINT fk_assignments_member
    FOREIGN KEY (member_id) REFERENCES members (id),
  CONSTRAINT fk_assignments_session
    FOREIGN KEY (session_id) REFERENCES sessions (id)
);

CREATE TABLE assignment_completions (
  id BIGINT NOT NULL AUTO_INCREMENT,
  assignment_id BIGINT NOT NULL,
  checked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(30) NOT NULL DEFAULT 'unchecked',
  note TEXT,
  PRIMARY KEY (id),
  CONSTRAINT fk_assignment_completions_assignment
    FOREIGN KEY (assignment_id) REFERENCES assignments (id)
);

CREATE TABLE reports (
  id BIGINT NOT NULL AUTO_INCREMENT,
  member_id BIGINT NOT NULL,
  session_id BIGINT,
  analysis_id BIGINT,
  report_title VARCHAR(150),
  workout_summary TEXT,
  posture_summary TEXT,
  good_points TEXT,
  caution_points TEXT,
  next_assignment TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_reports_member
    FOREIGN KEY (member_id) REFERENCES members (id),
  CONSTRAINT fk_reports_session
    FOREIGN KEY (session_id) REFERENCES sessions (id),
  CONSTRAINT fk_reports_analysis
    FOREIGN KEY (analysis_id) REFERENCES posture_analysis (id)
);
