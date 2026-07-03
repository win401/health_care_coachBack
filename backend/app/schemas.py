"""Pydantic 요청/응답 모델. 리소스가 추가될 때마다 이 파일에 이어서 정의한다."""

from typing import Optional

from pydantic import BaseModel, Field


# ---- Auth ----

class TrainerLoginRequest(BaseModel):
    login_id: str
    password: str


class MemberLoginRequest(BaseModel):
    name: str
    phone_last4: str = Field(min_length=4, max_length=4)


class AuthUserOut(BaseModel):
    id: int
    name: str
    role: str  # "trainer" | "member"


# ---- Members ----

class HealthNoteIn(BaseModel):
    pain_area: Optional[str] = None
    injury_history: Optional[str] = None
    precautions: Optional[str] = None
    asymmetry_note: Optional[str] = None


class MemberCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    fitness_goal: str
    exercise_experience: Optional[str] = None
    health_note: Optional[HealthNoteIn] = None
    consent_agreed: bool = False


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    fitness_goal: Optional[str] = None
    exercise_experience: Optional[str] = None
    status: Optional[str] = None


class MemberOut(BaseModel):
    id: int
    trainer_id: int
    name: str
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    fitness_goal: Optional[str] = None
    exercise_experience: Optional[str] = None
    status: str
    created_at: str


class MemberSummaryOut(BaseModel):
    member: MemberOut
    pain_area: Optional[str] = None
    precautions: Optional[str] = None
    injury_history: Optional[str] = None
    last_session_date: Optional[str] = None
    last_session_focus: Optional[str] = None
    last_posture_score: Optional[int] = None
    last_posture_main_issue: Optional[str] = None
    open_assignment_count: int = 0


# ---- Sessions ----

class SessionExerciseIn(BaseModel):
    exercise_name: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    note: Optional[str] = None


class SessionCreate(BaseModel):
    member_id: int
    session_date: str
    focus_area: Optional[str] = None
    memo: Optional[str] = None
    next_memo: Optional[str] = None
    raw_voice_text: Optional[str] = None
    summary: Optional[str] = None
    exercises: list[SessionExerciseIn] = Field(default_factory=list)


class SessionUpdate(BaseModel):
    focus_area: Optional[str] = None
    memo: Optional[str] = None
    next_memo: Optional[str] = None
    raw_voice_text: Optional[str] = None
    summary: Optional[str] = None


class SessionOut(BaseModel):
    id: int
    member_id: int
    trainer_id: int
    session_date: str
    focus_area: Optional[str] = None
    memo: Optional[str] = None
    next_memo: Optional[str] = None
    raw_voice_text: Optional[str] = None
    summary: Optional[str] = None
    created_at: str
    exercises: list[SessionExerciseIn] = Field(default_factory=list)


class VoiceSummaryRequest(BaseModel):
    raw_text: str


class VoiceSummaryOut(BaseModel):
    exercise_summary: str
    caution_note: str
    assignment_candidate: str


class VoiceRecordingOut(BaseModel):
    transcribed: bool
    raw_voice_text: Optional[str] = None
    exercise_summary: Optional[str] = None
    caution_note: Optional[str] = None
    assignment_candidate: Optional[str] = None
    message: Optional[str] = None


# ---- Assignments ----

class AssignmentCreate(BaseModel):
    member_id: int
    session_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    target_amount: Optional[str] = None
    due_date: Optional[str] = None
    status: str = "unchecked"


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None


class AssignmentOut(BaseModel):
    id: int
    member_id: int
    session_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    target_amount: Optional[str] = None
    due_date: Optional[str] = None
    status: str
    created_at: str
    completed_at: Optional[str] = None


# ---- Posture ----

class PostureAnalysisOut(BaseModel):
    id: int
    posture_image_id: int
    model_name: Optional[str] = None
    movement_name: Optional[str] = None
    analysis_status: str
    main_issue: Optional[str] = None
    sub_issue: Optional[str] = None
    result_note: Optional[str] = None
    analyzed_at: Optional[str] = None
    total_score: Optional[int] = None
    knee_alignment_score: Optional[int] = None
    upper_body_score: Optional[int] = None
    pelvis_balance_score: Optional[int] = None
    lower_body_stability_score: Optional[int] = None
    improvement_points: Optional[str] = None


class PostureImageOut(BaseModel):
    id: int
    member_id: int
    session_id: Optional[int] = None
    movement_name: Optional[str] = None
    image_path: str
    upload_status: str
    uploaded_at: str
    analysis: Optional[PostureAnalysisOut] = None


# ---- Feedbacks ----

class FeedbackCreate(BaseModel):
    member_id: int
    session_id: Optional[int] = None
    analysis_id: Optional[int] = None
    trainer_comment: str
    caution_note: Optional[str] = None
    next_check_point: Optional[str] = None


class FeedbackOut(BaseModel):
    id: int
    member_id: int
    session_id: Optional[int] = None
    analysis_id: Optional[int] = None
    trainer_comment: str
    caution_note: Optional[str] = None
    next_check_point: Optional[str] = None
    created_at: str


# ---- Reports ----

class ReportCreate(BaseModel):
    member_id: int
    session_id: Optional[int] = None
    analysis_id: Optional[int] = None
    report_title: Optional[str] = None


class ReportOut(BaseModel):
    id: int
    member_id: int
    session_id: Optional[int] = None
    analysis_id: Optional[int] = None
    report_title: Optional[str] = None
    workout_summary: Optional[str] = None
    posture_summary: Optional[str] = None
    good_points: Optional[str] = None
    caution_points: Optional[str] = None
    next_assignment: Optional[str] = None
    created_at: str


# ---- Trainer Daily Tasks (오늘의 일정표) ----

class TaskCreate(BaseModel):
    task_date: str
    time_label: Optional[str] = None
    title: str
    notes: Optional[str] = None


class TaskUpdate(BaseModel):
    time_label: Optional[str] = None
    title: Optional[str] = None
    notes: Optional[str] = None
    is_done: Optional[bool] = None


class TaskOut(BaseModel):
    id: int
    trainer_id: int
    task_date: str
    time_label: Optional[str] = None
    title: str
    notes: Optional[str] = None
    is_done: bool
    sort_order: int
    created_at: str
