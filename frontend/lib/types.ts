export type Member = {
  id: number;
  trainer_id: number;
  name: string;
  phone: string | null;
  age: number | null;
  gender: string | null;
  fitness_goal: string | null;
  exercise_experience: string | null;
  status: string;
  created_at: string;
};

export type MemberSummary = {
  member: Member;
  pain_area: string | null;
  precautions: string | null;
  injury_history: string | null;
  last_session_date: string | null;
  last_session_focus: string | null;
  last_posture_score: number | null;
  last_posture_main_issue: string | null;
  open_assignment_count: number;
};

export type SessionExercise = {
  exercise_name: string;
  sets: number | null;
  reps: number | null;
  weight_kg: number | null;
  note: string | null;
};

export type Session = {
  id: number;
  member_id: number;
  trainer_id: number;
  session_date: string;
  focus_area: string | null;
  memo: string | null;
  next_memo: string | null;
  raw_voice_text: string | null;
  summary: string | null;
  created_at: string;
  exercises: SessionExercise[];
};

export type Assignment = {
  id: number;
  member_id: number;
  session_id: number | null;
  title: string;
  description: string | null;
  target_amount: string | null;
  due_date: string | null;
  status: string;
  created_at: string;
  completed_at: string | null;
};

export type PostureAnalysis = {
  id: number;
  posture_image_id: number;
  model_name: string | null;
  movement_name: string | null;
  analysis_status: string;
  main_issue: string | null;
  sub_issue: string | null;
  result_note: string | null;
  analyzed_at: string | null;
  total_score: number | null;
  knee_alignment_score: number | null;
  upper_body_score: number | null;
  pelvis_balance_score: number | null;
  lower_body_stability_score: number | null;
  improvement_points: string | null;
};

export type PostureImage = {
  id: number;
  member_id: number;
  session_id: number | null;
  movement_name: string | null;
  image_path: string;
  upload_status: string;
  uploaded_at: string;
  analysis: PostureAnalysis | null;
};

export type Feedback = {
  id: number;
  member_id: number;
  session_id: number | null;
  analysis_id: number | null;
  trainer_comment: string;
  caution_note: string | null;
  next_check_point: string | null;
  created_at: string;
};

export type Report = {
  id: number;
  member_id: number;
  session_id: number | null;
  analysis_id: number | null;
  report_title: string | null;
  workout_summary: string | null;
  posture_summary: string | null;
  good_points: string | null;
  caution_points: string | null;
  next_assignment: string | null;
  created_at: string;
};

export type PostureHistoryPoint = {
  analyzed_at: string;
  total_score: number | null;
  knee_alignment_score: number | null;
  upper_body_score: number | null;
  pelvis_balance_score: number | null;
  lower_body_stability_score: number | null;
  main_issue: string | null;
};

export type TrainerTask = {
  id: number;
  trainer_id: number;
  task_date: string;
  time_label: string | null;
  title: string;
  notes: string | null;
  is_done: boolean;
  sort_order: number;
  created_at: string;
};

export type VoiceRecordingSummary = {
  transcribed: boolean;
  raw_voice_text: string | null;
  exercise_summary: string | null;
  caution_note: string | null;
  assignment_candidate: string | null;
  message: string | null;
};
