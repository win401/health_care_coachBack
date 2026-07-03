from __future__ import annotations

import os
import re
import sqlite3
import threading
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
os.environ.setdefault("MPLBACKEND", "Agg")

import gradio as gr
import pandas as pd

from ai_service import generate_report_parts, summarize_session_note
from pose_service import COCO_KEYPOINTS, analyze_pose, save_annotated_image


COLAB_SOURCE = ROOT / "fitnote-trainer-colab-sample-queries.py"


def _extract_sql_block(variable_name: str) -> str:
    source = COLAB_SOURCE.read_text(encoding="utf-8")
    pattern = rf'{variable_name}\s*=\s*"""(.*?)"""'
    match = re.search(pattern, source, flags=re.DOTALL)
    if not match:
        raise RuntimeError(f"{variable_name} block not found in {COLAB_SOURCE.name}")
    return match.group(1)


def create_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(_extract_sql_block("schema_sql"))
    conn.executescript(_extract_sql_block("sample_data_sql"))
    return conn


CONN = create_connection()
DB_LOCK = threading.RLock()


def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    with DB_LOCK:
        return pd.read_sql_query(sql, CONN, params=params)


def scalar(sql: str, params: tuple = ()):
    with DB_LOCK:
        return CONN.execute(sql, params).fetchone()[0]


def member_options() -> list[str]:
    with DB_LOCK:
        rows = CONN.execute("SELECT id, name FROM members ORDER BY id").fetchall()
    return [f"{row[0]} - {row[1]}" for row in rows]


def parse_member_id(member_label: str) -> int:
    return int(member_label.split(" - ", 1)[0])


def selected_file_path(file_value) -> str | None:
    if file_value is None:
        return None
    if isinstance(file_value, str):
        return file_value
    return getattr(file_value, "name", None)


def keypoints_dataframe(keypoints: list[dict[str, float | int | str]]) -> pd.DataFrame:
    if not keypoints:
        return pd.DataFrame(columns=["keypoint_index", "point_name", "x", "y", "confidence"])
    return pd.DataFrame(keypoints)[["keypoint_index", "point_name", "x", "y", "confidence"]]


def keypoints_from_dataframe(keypoints_df) -> list[dict[str, float | int | str]]:
    if keypoints_df is None:
        return []

    df = keypoints_df if isinstance(keypoints_df, pd.DataFrame) else pd.DataFrame(keypoints_df)
    if df.empty:
        return []

    keypoints: list[dict[str, float | int | str]] = []
    for _, row in df.iterrows():
        try:
            index = int(row["keypoint_index"])
            point_name = str(row.get("point_name") or COCO_KEYPOINTS[index])
            keypoints.append(
                {
                    "keypoint_index": index,
                    "point_name": point_name,
                    "x": round(float(row["x"]), 3),
                    "y": round(float(row["y"]), 3),
                    "confidence": round(float(row.get("confidence", 1.0)), 4),
                }
            )
        except Exception:
            continue
    return keypoints


def analyze_standing_posture_preview(standing_posture_image):
    image_path = selected_file_path(standing_posture_image)
    if not image_path:
        return (
            None,
            "**정자세 YOLO 상태:** 이미지를 업로드하면 관절 포인트와 스켈레톤을 표시합니다.",
            keypoints_dataframe([]),
        )

    pose_result = analyze_pose(image_path, "정자세 프로필")
    status = (
        f"**정자세 YOLO 상태:** {pose_result.analysis_status} / "
        f"keypoint {len(pose_result.keypoints)}개 / "
        f"{'스켈레톤 이미지 생성됨' if pose_result.annotated_image_path else '스켈레톤 이미지 없음'}"
    )
    return pose_result.annotated_image_path, status, keypoints_dataframe(pose_result.keypoints)


def redraw_standing_skeleton(standing_posture_image, keypoints_df):
    image_path = selected_file_path(standing_posture_image)
    if not image_path:
        return None, "**정자세 YOLO 상태:** 수정할 원본 이미지가 없습니다."

    keypoints = keypoints_from_dataframe(keypoints_df)
    if not keypoints:
        return None, "**정자세 YOLO 상태:** 수정할 관절 좌표가 없습니다."

    annotated_path = save_annotated_image(image_path, keypoints, suffix="trainer_adjusted_skeleton")
    status = (
        f"**정자세 YOLO 상태:** 트레이너 수정 반영 / "
        f"keypoint {len(keypoints)}개 / "
        f"{'스켈레톤 이미지 생성됨' if annotated_path else '스켈레톤 이미지 없음'}"
    )
    return annotated_path, status


def month_calendar_card() -> str:
    today = date.today()
    first_day = today.replace(day=1)
    start_weekday = first_day.weekday()
    next_month = today.replace(year=today.year + 1, month=1, day=1) if today.month == 12 else today.replace(month=today.month + 1, day=1)
    last_day = (next_month - timedelta(days=1)).day

    cells = [""] * start_weekday + [str(day) for day in range(1, last_day + 1)]
    while len(cells) % 7:
        cells.append("")

    rows = []
    for index in range(0, len(cells), 7):
        days = []
        for value in cells[index : index + 7]:
            class_name = "today" if value and int(value) == today.day else ""
            days.append(f'<td class="{class_name}">{value}</td>')
        rows.append("<tr>" + "".join(days) + "</tr>")

    return f"""
<div class="mini-calendar">
  <div class="calendar-title">{today.year}년 {today.month}월</div>
  <table>
    <thead><tr><th>월</th><th>화</th><th>수</th><th>목</th><th>금</th><th>토</th><th>일</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</div>
"""


def render_kpis() -> str:
    total_members = scalar("SELECT COUNT(*) FROM members")
    total_sessions = scalar("SELECT COUNT(*) FROM sessions")
    open_assignments = scalar("SELECT COUNT(*) FROM assignments WHERE status != 'completed'")
    avg_score = scalar("SELECT ROUND(AVG(total_score), 1) FROM posture_scores")
    consent_pending = scalar("SELECT COUNT(*) FROM member_consents WHERE is_agreed = 0")

    return f"""
<div class="kpi-grid">
  <div class="kpi-card"><span>등록 회원</span><strong>{total_members}</strong></div>
  <div class="kpi-card"><span>누적 세션</span><strong>{total_sessions}</strong></div>
  <div class="kpi-card"><span>미완료 과제</span><strong>{open_assignments}</strong></div>
  <div class="kpi-card"><span>평균 자세 점수</span><strong>{avg_score}</strong></div>
  <div class="kpi-card warn"><span>동의 미확인</span><strong>{consent_pending}</strong></div>
</div>
"""


def recent_sessions() -> pd.DataFrame:
    return query(
        """
        SELECT
          s.session_date AS 수업일,
          m.name AS 회원,
          t.name AS 트레이너,
          s.focus_area AS 운동부위,
          s.summary AS 세션요약
        FROM sessions s
        JOIN members m ON s.member_id = m.id
        JOIN trainers t ON s.trainer_id = t.id
        ORDER BY s.session_date DESC, s.id DESC
        LIMIT 8;
        """
    )


def risk_members() -> pd.DataFrame:
    return query(
        """
        SELECT
          m.name AS 회원,
          COALESCE(h.pain_area, '-') AS 통증부위,
          COALESCE(h.precautions, '-') AS 수업주의사항,
          COALESCE(ROUND(AVG(ps.total_score), 1), '-') AS 평균자세점수
        FROM members m
        LEFT JOIN member_health_notes h ON m.id = h.member_id
        LEFT JOIN posture_images pi ON m.id = pi.member_id
        LEFT JOIN posture_analysis pa ON pi.id = pa.posture_image_id
        LEFT JOIN posture_scores ps ON pa.id = ps.analysis_id
        GROUP BY m.id, m.name, h.pain_area, h.precautions
        ORDER BY
          CASE WHEN AVG(ps.total_score) IS NULL THEN 999 ELSE AVG(ps.total_score) END ASC,
          m.id ASC;
        """
    )


def open_assignments() -> pd.DataFrame:
    return query(
        """
        SELECT
          m.name AS 회원,
          a.title AS 과제명,
          a.target_amount AS 목표량,
          a.due_date AS 마감일,
          a.status AS 상태
        FROM assignments a
        JOIN members m ON a.member_id = m.id
        WHERE a.status != 'completed'
        ORDER BY a.due_date ASC;
        """
    )


def posture_summary() -> pd.DataFrame:
    return query(
        """
        SELECT
          m.name AS 회원,
          pa.movement_name AS 동작,
          pa.model_name AS 모델명,
          pa.analysis_status AS 분석상태,
          COUNT(DISTINCT pk.id) AS Keypoint수,
          ps.total_score AS 총점,
          pa.main_issue AS 주요문제,
          ps.improvement_points AS 개선항목,
          pa.analyzed_at AS 분석일시
        FROM posture_scores ps
        JOIN posture_analysis pa ON ps.analysis_id = pa.id
        JOIN posture_images pi ON pa.posture_image_id = pi.id
        JOIN members m ON pi.member_id = m.id
        LEFT JOIN posture_keypoints pk ON pa.id = pk.analysis_id
        GROUP BY
          m.name,
          pa.movement_name,
          pa.model_name,
          pa.analysis_status,
          ps.total_score,
          pa.main_issue,
          ps.improvement_points,
          pa.analyzed_at
        ORDER BY ps.total_score ASC;
        """
    )


def member_profile(member_label: str):
    member_id = parse_member_id(member_label)
    profile = query(
        """
        SELECT
          m.name AS 회원명,
          m.age AS 나이,
          m.gender AS 성별,
          m.fitness_goal AS 운동목표,
          m.exercise_experience AS 운동경험,
          b.height_cm AS 키_cm,
          b.weight_kg AS 체중_kg,
          b.body_type_note AS 신체특성,
          h.pain_area AS 통증부위,
          h.injury_history AS 부상이력,
          h.precautions AS 수업주의사항,
          h.asymmetry_note AS 비대칭메모,
          c.is_agreed AS 정보수집동의
        FROM members m
        LEFT JOIN member_body_profiles b ON m.id = b.member_id
        LEFT JOIN member_health_notes h ON m.id = h.member_id
        LEFT JOIN member_consents c ON m.id = c.member_id
        WHERE m.id = ?;
        """,
        (member_id,),
    )
    sessions = query(
        """
        SELECT
          session_date AS 수업일,
          focus_area AS 운동부위,
          summary AS 요약,
          next_memo AS 다음메모
        FROM sessions
        WHERE member_id = ?
        ORDER BY session_date DESC;
        """,
        (member_id,),
    )
    assignments = query(
        """
        SELECT
          title AS 과제명,
          target_amount AS 목표량,
          due_date AS 마감일,
          status AS 상태,
          completed_at AS 완료일시
        FROM assignments
        WHERE member_id = ?
        ORDER BY due_date ASC;
        """,
        (member_id,),
    )
    return profile, sessions, assignments


def today_sessions(member_label: str) -> pd.DataFrame:
    member_id = parse_member_id(member_label)
    today_text = date.today().isoformat()
    return query(
        """
        SELECT
          s.session_date AS 수업일,
          s.focus_area AS 수업주제,
          COALESCE(s.memo, '-') AS 메모,
          COALESCE(s.next_memo, '-') AS 다음확인
        FROM sessions s
        WHERE s.member_id = ? AND s.session_date = ?
        ORDER BY s.id DESC;
        """,
        (member_id, today_text),
    )


def today_exercise_options(member_label: str) -> list[str]:
    member_id = parse_member_id(member_label)
    rows = CONN.execute(
        """
        SELECT DISTINCT se.exercise_name
        FROM session_exercises se
        JOIN sessions s ON se.session_id = s.id
        WHERE s.member_id = ?
        ORDER BY se.id DESC
        LIMIT 8;
        """,
        (member_id,),
    ).fetchall()
    exercises = [row[0] for row in rows]
    if exercises:
        return exercises
    return ["스쿼트", "런지", "힙힌지", "플랭크", "고관절 스트레칭"]


def home_member_dashboard(member_label: str):
    profile, sessions, assignments = member_profile(member_label)
    member_id = parse_member_id(member_label)
    posture = query(
        """
        SELECT
          pa.analyzed_at AS 분석일시,
          pa.movement_name AS 동작,
          pa.model_name AS 모델명,
          pa.analysis_status AS 분석상태,
          COUNT(DISTINCT pk.id) AS Keypoint수,
          ps.total_score AS 총점,
          pa.main_issue AS 주요문제,
          ps.improvement_points AS 개선항목
        FROM posture_scores ps
        JOIN posture_analysis pa ON ps.analysis_id = pa.id
        JOIN posture_images pi ON pa.posture_image_id = pi.id
        LEFT JOIN posture_keypoints pk ON pa.id = pk.analysis_id
        WHERE pi.member_id = ?
        GROUP BY
          pa.analyzed_at,
          pa.movement_name,
          pa.model_name,
          pa.analysis_status,
          ps.total_score,
          pa.main_issue,
          ps.improvement_points,
          pa.id
        ORDER BY pa.analyzed_at DESC, pa.id DESC
        LIMIT 5;
        """,
        (member_id,),
    )
    open_member_assignments = query(
        """
        SELECT
          title AS 과제명,
          target_amount AS 목표량,
          due_date AS 마감일,
          status AS 상태
        FROM assignments
        WHERE member_id = ? AND status != 'completed'
        ORDER BY due_date ASC;
        """,
        (member_id,),
    )
    summary = profile.iloc[0].to_dict() if not profile.empty else {}
    summary_card = f"""
<div class="summary-card">
  <h3>{summary.get('회원명', '-')}</h3>
  <p><strong>운동 목표</strong><br>{summary.get('운동목표', '-')}</p>
  <p><strong>통증/주의사항</strong><br>{summary.get('통증부위', '-') or '-'} / {summary.get('수업주의사항', '-') or '-'}</p>
  <p><strong>비대칭/가동성 메모</strong><br>{summary.get('비대칭메모', '-') or '-'}</p>
  <p><strong>정보 수집 동의</strong><br>{'동의' if summary.get('정보수집동의') == 1 else '미동의 또는 미확인'}</p>
</div>
"""
    return (
        month_calendar_card(),
        today_sessions(member_label),
        summary_card,
        sessions.head(5),
        posture,
        open_member_assignments,
        gr.update(choices=today_exercise_options(member_label), value=[]),
    )


def member_report(member_label: str):
    member_id = parse_member_id(member_label)
    reports = query(
        """
        SELECT
          r.report_title AS 리포트제목,
          r.workout_summary AS 운동요약,
          r.posture_summary AS 자세요약,
          r.good_points AS 잘한점,
          r.caution_points AS 주의점,
          r.next_assignment AS 다음과제,
          r.created_at AS 생성일시
        FROM reports r
        WHERE r.member_id = ?
        ORDER BY r.id DESC;
        """,
        (member_id,),
    )
    scores = query(
        """
        SELECT
          s.session_date AS 수업일,
          pa.movement_name AS 동작,
          ps.total_score AS 총점,
          ps.knee_alignment_score AS 무릎정렬,
          ps.upper_body_score AS 상체,
          ps.pelvis_balance_score AS 골반,
          ps.lower_body_stability_score AS 하체안정성
        FROM posture_scores ps
        JOIN posture_analysis pa ON ps.analysis_id = pa.id
        JOIN posture_images pi ON pa.posture_image_id = pi.id
        LEFT JOIN sessions s ON pi.session_id = s.id
        WHERE pi.member_id = ?
        ORDER BY s.session_date ASC;
        """,
        (member_id,),
    )
    keypoints = query(
        """
        SELECT
          pa.movement_name AS 동작,
          pk.keypoint_index AS YOLO번호,
          pk.point_name AS 관절명,
          pk.x AS X좌표,
          pk.y AS Y좌표,
          pk.confidence AS 신뢰도
        FROM posture_keypoints pk
        JOIN posture_analysis pa ON pk.analysis_id = pa.id
        JOIN posture_images pi ON pa.posture_image_id = pi.id
        WHERE pi.member_id = ?
        ORDER BY pa.id, pk.keypoint_index;
        """,
        (member_id,),
    )
    return reports, scores, keypoints


def session_options(member_label: str) -> list[str]:
    member_id = parse_member_id(member_label)
    rows = CONN.execute(
        """
        SELECT id, session_date, COALESCE(focus_area, '운동')
        FROM sessions
        WHERE member_id = ?
        ORDER BY session_date DESC, id DESC;
        """,
        (member_id,),
    ).fetchall()
    return [f"{row[0]} - {row[1]} - {row[2]}" for row in rows]


def parse_session_id(session_label: str | None) -> int | None:
    if not session_label:
        return None
    return int(session_label.split(" - ", 1)[0])


def summarize_voice_with_status(raw_voice_text: str) -> tuple[str, str]:
    text = (raw_voice_text or "").strip()
    if not text:
        return (
            "음성 메모 텍스트를 입력하면 운동 내용, 주의사항, 다음 과제를 요약합니다.",
            "**AI 분석 상태:** 대기 중",
        )

    ai_summary = summarize_session_note(text)
    if ai_summary:
        return ai_summary, "**AI 분석 상태:** OpenAI API 사용됨"

    lower_text = text.lower()
    caution_keywords = ["통증", "무릎", "허리", "어깨", "불편", "주의"]
    assignment_keywords = ["숙제", "과제", "집에서", "스트레칭", "다음"]
    cautions = [word for word in caution_keywords if word in lower_text or word in text]
    assignments = [word for word in assignment_keywords if word in lower_text or word in text]

    caution_line = ", ".join(cautions) if cautions else "특이 통증 언급 없음"
    assignment_line = "홈트레이닝/스트레칭 과제 후보 있음" if assignments else "별도 과제 언급 없음"
    fallback_summary = (
        f"- 운동 내용: {text[:80]}{'...' if len(text) > 80 else ''}\n"
        f"- 주의사항 키워드: {caution_line}\n"
        f"- 다음 과제 후보: {assignment_line}"
    )
    return fallback_summary, "**AI 분석 상태:** fallback 사용됨 - API 키, 네트워크, 응답 형식 중 하나를 확인하세요."


def summarize_voice(raw_voice_text: str) -> str:
    return summarize_voice_with_status(raw_voice_text)[0]


def register_member(
    name: str,
    phone: str,
    age: int | None,
    gender: str,
    fitness_goal: str,
    exercise_experience: str,
    inbody_image,
    standing_posture_image,
    mobility_note: str,
    shoulder_asymmetry: bool,
    pelvis_asymmetry: bool,
    other_asymmetry: str,
    pain_area: str,
    injury_history: str,
    precautions: str,
    consent_agreed: bool,
):
    if not name:
        return "회원 이름은 필수입니다.", gr.update(), gr.update(), gr.update(), gr.update()

    trainer_id = scalar("SELECT id FROM trainers ORDER BY id LIMIT 1")
    cursor = CONN.execute(
        """
        INSERT INTO members
        (trainer_id, name, phone, age, gender, fitness_goal, exercise_experience)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (trainer_id, name, phone, age, gender, fitness_goal, exercise_experience),
    )
    member_id = cursor.lastrowid
    CONN.execute(
        """
        INSERT INTO member_body_profiles
        (member_id, body_type_note)
        VALUES (?, ?);
        """,
        (
            member_id,
            f"인바디 이미지: {selected_file_path(inbody_image) or '미등록'} / 가동성 체크: {mobility_note or '미입력'}",
        ),
    )
    asymmetry_items = []
    if shoulder_asymmetry:
        asymmetry_items.append("어깨")
    if pelvis_asymmetry:
        asymmetry_items.append("골반")
    if other_asymmetry:
        asymmetry_items.append(f"기타: {other_asymmetry}")
    asymmetry_note = ", ".join(asymmetry_items) if asymmetry_items else "특이 비대칭 없음"
    CONN.execute(
        """
        INSERT INTO member_health_notes
        (member_id, pain_area, injury_history, precautions, asymmetry_note)
        VALUES (?, ?, ?, ?, ?);
        """,
        (member_id, pain_area, injury_history, precautions, asymmetry_note),
    )
    standing_path = selected_file_path(standing_posture_image)
    if standing_path:
        CONN.execute(
            """
            INSERT INTO posture_images
            (member_id, movement_name, image_path)
            VALUES (?, '정자세 프로필', ?);
            """,
            (member_id, standing_path),
        )
    CONN.execute(
        """
        INSERT INTO member_consents
        (member_id, consent_type, consent_text, is_agreed, agreed_at)
        VALUES (?, 'personal_health_data', '운동 목표와 통증/자세 분석 정보 수집 안내', ?, DATETIME('now', 'localtime'));
        """,
        (member_id, 1 if consent_agreed else 0),
    )
    CONN.commit()
    choices = member_options()
    selected = f"{member_id} - {name}"
    update = gr.update(choices=choices, value=selected)
    return f"{name} 회원이 저장되었습니다.", update, update, update, gr.update(choices=[], value=None)


def start_session_from_home(member_label: str, checked_exercises: list[str], memo: str):
    checked = ", ".join(checked_exercises) if checked_exercises else "선택 운동 없음"
    message = f"세션 시작 준비 완료: {checked}\n\n`수업 기록 / 자세 분석 / 과제` 탭으로 이동해서 이어서 기록하세요."
    session_memo = f"홈 대시보드 메모: {memo or '-'}\n오늘 진행 예정 운동: {checked}"
    return (
        message,
        gr.update(value=member_label),
        gr.update(value=checked),
        gr.update(value=session_memo),
    )


def member_portal(member_label: str):
    profile, _, assignments = member_profile(member_label)
    member_id = parse_member_id(member_label)
    summary = profile.iloc[0].to_dict() if not profile.empty else {}
    profile_card = f"""
<div class="summary-card">
  <h3>{summary.get('회원명', '-')} 회원 화면</h3>
  <p><strong>운동 목표</strong><br>{summary.get('운동목표', '-')}</p>
  <p><strong>주의사항</strong><br>{summary.get('통증부위', '-') or '-'} / {summary.get('수업주의사항', '-') or '-'}</p>
  <p><strong>남은 세션</strong><br>8회</p>
</div>
"""
    schedules = query(
        """
        SELECT
          session_date AS 일정일,
          focus_area AS 예약내용,
          COALESCE(next_memo, '-') AS 메모
        FROM sessions
        WHERE member_id = ?
        ORDER BY session_date DESC
        LIMIT 10;
        """,
        (member_id,),
    )
    history = query(
        """
        SELECT
          s.session_date AS 날짜,
          s.focus_area AS 수업내용,
          COALESCE(s.summary, '-') AS 기록
        FROM sessions s
        WHERE s.member_id = ?
        ORDER BY s.session_date ASC;
        """,
        (member_id,),
    )
    posture_scores = query(
        """
        SELECT
          COALESCE(s.session_date, DATE(pa.analyzed_at)) AS 날짜,
          pa.movement_name AS 동작,
          ps.total_score AS 점수
        FROM posture_scores ps
        JOIN posture_analysis pa ON ps.analysis_id = pa.id
        JOIN posture_images pi ON pa.posture_image_id = pi.id
        LEFT JOIN sessions s ON pi.session_id = s.id
        WHERE pi.member_id = ?
        ORDER BY 날짜 ASC;
        """,
        (member_id,),
    )
    weight_history = query(
        """
        SELECT
          DATE(created_at) AS 날짜,
          weight_kg AS 몸무게
        FROM member_body_profiles
        WHERE member_id = ? AND weight_kg IS NOT NULL
        ORDER BY created_at ASC;
        """,
        (member_id,),
    )
    if weight_history.empty:
        weight_history = pd.DataFrame(
            {
                "날짜": ["2026-07-01", "2026-07-08", "2026-07-15", "2026-07-22"],
                "몸무게": [72.4, 71.8, 71.2, 70.9],
            }
        )
    attendance = query(
        """
        SELECT session_date AS 출석일, focus_area AS 수업내용
        FROM sessions
        WHERE member_id = ?
        ORDER BY session_date DESC;
        """,
        (member_id,),
    )
    calendar = f"""
<div class="summary-card">
  <h3>이번 달 출석 요약</h3>
  <p><strong>한달 출석률</strong><br>75%</p>
  <p><strong>남은 세션</strong><br>8회</p>
  <p><strong>다음 PT 예약</strong><br>{schedules.iloc[0]['일정일'] if not schedules.empty else '예약 없음'}</p>
</div>
"""
    return (
        profile_card,
        assignments,
        schedules,
        history,
        posture_scores,
        weight_history,
        calendar,
        attendance,
    )


def save_training_flow(
    member_label: str,
    session_date: str,
    focus_area: str,
    session_memo: str,
    raw_voice_text: str,
    posture_image_path: str | None,
    movement_name: str,
    trainer_comment: str,
    assignment_title: str,
    assignment_description: str,
    target_amount: str,
    due_date: str,
):
    member_id = parse_member_id(member_label)
    trainer_id = scalar("SELECT trainer_id FROM members WHERE id = ?", (member_id,))
    voice_summary, voice_status = summarize_voice_with_status(raw_voice_text)
    summary = f"{focus_area or '운동'} 세션. {voice_summary.replace(chr(10), ' ')}"
    cursor = CONN.execute(
        """
        INSERT INTO sessions
        (member_id, trainer_id, session_date, focus_area, memo, next_memo, raw_voice_text, summary)
        VALUES (?, ?, COALESCE(NULLIF(?, ''), DATE('now', 'localtime')), ?, ?, ?, ?, ?);
        """,
        (
            member_id,
            trainer_id,
            session_date,
            focus_area,
            session_memo,
            assignment_title or "다음 수업 전 과제 수행 여부 확인",
            raw_voice_text,
            summary,
        ),
    )
    session_id = cursor.lastrowid

    analysis_id = None
    annotated_image_path = None
    posture_visual_status = "**YOLO 시각화 상태:** 자세 이미지를 업로드하면 관절 포인트와 스켈레톤을 표시합니다."
    if posture_image_path:
        pose_result = analyze_pose(posture_image_path, movement_name or focus_area or "자세 분석")
        annotated_image_path = pose_result.annotated_image_path
        posture_visual_status = (
            f"**YOLO 시각화 상태:** {pose_result.analysis_status} / "
            f"keypoint {len(pose_result.keypoints)}개 / "
            f"{'스켈레톤 이미지 생성됨' if annotated_image_path else '스켈레톤 이미지 없음'}"
        )
        image_cursor = CONN.execute(
            """
            INSERT INTO posture_images
            (member_id, session_id, movement_name, image_path, upload_status)
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                member_id,
                session_id,
                movement_name or focus_area or "자세 분석",
                posture_image_path,
                "analyzed" if pose_result.analysis_status in {"success", "fallback"} else "uploaded",
            ),
        )
        posture_image_id = image_cursor.lastrowid
        analysis_cursor = CONN.execute(
            """
            INSERT INTO posture_analysis
            (posture_image_id, model_name, movement_name, analysis_status, main_issue, sub_issue, result_note, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, DATETIME('now', 'localtime'));
            """,
            (
                posture_image_id,
                pose_result.model_name,
                movement_name or focus_area or "스쿼트",
                pose_result.analysis_status,
                pose_result.main_issue,
                pose_result.sub_issue,
                pose_result.result_note,
            ),
        )
        analysis_id = analysis_cursor.lastrowid
        for point in pose_result.keypoints:
            CONN.execute(
                """
                INSERT INTO posture_keypoints
                (analysis_id, keypoint_index, point_name, x, y, confidence)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    analysis_id,
                    point["keypoint_index"],
                    point["point_name"],
                    point["x"],
                    point["y"],
                    point["confidence"],
                ),
            )
        CONN.execute(
            """
            INSERT INTO posture_scores
            (analysis_id, total_score, knee_alignment_score, upper_body_score, pelvis_balance_score, lower_body_stability_score, improvement_points)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                analysis_id,
                pose_result.total_score,
                pose_result.knee_alignment_score,
                pose_result.upper_body_score,
                pose_result.pelvis_balance_score,
                pose_result.lower_body_stability_score,
                pose_result.improvement_points,
            ),
        )

    if trainer_comment:
        CONN.execute(
            """
            INSERT INTO feedbacks
            (member_id, session_id, analysis_id, trainer_comment, caution_note, next_check_point)
            VALUES (?, ?, ?, ?, '통증 부위 반응 확인', '다음 수업에서 자세와 과제 수행 여부 재확인');
            """,
            (member_id, session_id, analysis_id, trainer_comment),
        )

    if assignment_title:
        CONN.execute(
            """
            INSERT INTO assignments
            (member_id, session_id, title, description, target_amount, due_date, status)
            VALUES (?, ?, ?, ?, ?, ?, 'in_progress');
            """,
            (member_id, session_id, assignment_title, assignment_description, target_amount, due_date),
        )

    CONN.commit()
    sessions = session_options(member_label)
    return (
        f"전체 저장 완료: 세션 #{session_id}이 생성되었습니다.",
        voice_summary,
        voice_status,
        annotated_image_path,
        posture_visual_status,
        member_profile(member_label)[1],
        posture_summary(),
        member_profile(member_label)[2],
        gr.update(choices=sessions, value=sessions[0] if sessions else None),
    )


def update_session_dropdown(member_label: str):
    choices = session_options(member_label)
    return gr.update(choices=choices, value=choices[0] if choices else None)


def generate_report(member_label: str, session_label: str | None):
    member_id = parse_member_id(member_label)
    session_id = parse_session_id(session_label)
    if session_id is None:
        return "선택 가능한 세션이 없습니다.", "**AI 분석 상태:** 대기 중", member_report(member_label)[0]

    session = CONN.execute(
        "SELECT session_date, focus_area, summary FROM sessions WHERE id = ?",
        (session_id,),
    ).fetchone()
    analysis = CONN.execute(
        """
        SELECT pa.id, pa.movement_name, pa.main_issue, ps.total_score, ps.improvement_points
        FROM posture_analysis pa
        JOIN posture_images pi ON pa.posture_image_id = pi.id
        LEFT JOIN posture_scores ps ON pa.id = ps.analysis_id
        WHERE pi.session_id = ?
        ORDER BY pa.id DESC
        LIMIT 1;
        """,
        (session_id,),
    ).fetchone()
    feedback = CONN.execute(
        """
        SELECT trainer_comment, caution_note
        FROM feedbacks
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT 1;
        """,
        (session_id,),
    ).fetchone()
    assignment = CONN.execute(
        """
        SELECT title, target_amount, due_date
        FROM assignments
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT 1;
        """,
        (session_id,),
    ).fetchone()

    workout_summary = session[2] if session else "세션 기록 없음"
    posture_text = (
        f"{analysis[1]} 총점 {analysis[3]}점, {analysis[2]} / {analysis[4]}"
        if analysis
        else "자세 분석 기록 없음"
    )
    feedback_text = feedback[0] if feedback else "트레이너 피드백 없음"
    caution_text = feedback[1] if feedback else "주의사항 없음"
    assignment_text = (
        f"{assignment[0]} ({assignment[1]}, 마감 {assignment[2]})"
        if assignment
        else "다음 과제 없음"
    )
    member_name = member_label.split(" - ", 1)[1]
    ai_report = generate_report_parts(
        member_name=member_name,
        session_date=session[0] if session else "",
        workout_summary=workout_summary,
        posture_summary=posture_text,
        trainer_feedback=feedback_text,
        caution_note=caution_text,
        next_assignment=assignment_text,
    )
    report_status = (
        "**AI 분석 상태:** OpenAI API 사용됨"
        if ai_report
        else "**AI 분석 상태:** fallback 사용됨 - API 키, 네트워크, 응답 형식 중 하나를 확인하세요."
    )
    title = (
        ai_report["report_title"]
        if ai_report and ai_report.get("report_title")
        else f"{member_name} {session[0] if session else ''} 수업 리포트"
    )
    workout_summary = ai_report["workout_summary"] if ai_report and ai_report.get("workout_summary") else workout_summary
    posture_text = ai_report["posture_summary"] if ai_report and ai_report.get("posture_summary") else posture_text
    feedback_text = ai_report["good_points"] if ai_report and ai_report.get("good_points") else feedback_text
    caution_text = ai_report["caution_points"] if ai_report and ai_report.get("caution_points") else caution_text
    assignment_text = ai_report["next_assignment"] if ai_report and ai_report.get("next_assignment") else assignment_text
    CONN.execute(
        """
        INSERT INTO reports
        (member_id, session_id, analysis_id, report_title, workout_summary, posture_summary, good_points, caution_points, next_assignment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            member_id,
            session_id,
            analysis[0] if analysis else None,
            title,
            workout_summary,
            posture_text,
            feedback_text,
            caution_text,
            assignment_text,
        ),
    )
    CONN.commit()
    report_markdown = f"""
## {title}

**오늘의 운동 요약**
{workout_summary}

**자세 분석 결과**
{posture_text}

**트레이너 피드백**
{feedback_text}

**다음 과제**
{assignment_text}
"""
    return report_markdown, report_status, member_report(member_label)[0]


def render_admin_kpis() -> str:
    total_trainers = scalar("SELECT COUNT(*) FROM trainers")
    total_members = scalar("SELECT COUNT(*) FROM members")
    total_sessions = scalar("SELECT COUNT(*) FROM sessions")
    total_analyses = scalar("SELECT COUNT(*) FROM posture_analysis")
    total_reports = scalar("SELECT COUNT(*) FROM reports")
    total_assignments = scalar("SELECT COUNT(*) FROM assignments")
    completed_assignments = scalar(
        """
        SELECT COUNT(*)
        FROM assignments a
        LEFT JOIN assignment_completions ac ON a.id = ac.assignment_id
        WHERE a.status = 'completed' OR ac.status = 'completed';
        """
    )
    completion_rate = round((completed_assignments / total_assignments) * 100, 1) if total_assignments else 0

    return f"""
<div class="kpi-grid admin-kpi-grid">
  <div class="kpi-card"><span>트레이너</span><strong>{total_trainers}</strong></div>
  <div class="kpi-card"><span>회원</span><strong>{total_members}</strong></div>
  <div class="kpi-card"><span>누적 수업</span><strong>{total_sessions}</strong></div>
  <div class="kpi-card"><span>자세 분석</span><strong>{total_analyses}</strong></div>
  <div class="kpi-card"><span>리포트</span><strong>{total_reports}</strong></div>
  <div class="kpi-card warn"><span>과제 완료율</span><strong>{completion_rate}%</strong></div>
</div>
"""


def trainer_usage_summary() -> pd.DataFrame:
    return query(
        """
        SELECT
          t.name AS 트레이너,
          t.center_name AS 센터,
          COUNT(DISTINCT m.id) AS 담당회원수,
          COUNT(DISTINCT s.id) AS 수업기록수,
          COUNT(DISTINCT pa.id) AS 자세분석수,
          COUNT(DISTINCT a.id) AS 과제부여수,
          COUNT(DISTINCT r.id) AS 리포트생성수,
          COALESCE(MAX(s.session_date), '-') AS 최근수업일
        FROM trainers t
        LEFT JOIN members m ON t.id = m.trainer_id
        LEFT JOIN sessions s ON t.id = s.trainer_id
        LEFT JOIN assignments a ON m.id = a.member_id
        LEFT JOIN posture_images pi ON m.id = pi.member_id
        LEFT JOIN posture_analysis pa ON pi.id = pa.posture_image_id
        LEFT JOIN reports r ON m.id = r.member_id
        GROUP BY t.id, t.name, t.center_name
        ORDER BY 수업기록수 DESC, 담당회원수 DESC;
        """
    )


def member_usage_summary() -> pd.DataFrame:
    return query(
        """
        SELECT
          m.name AS 회원,
          t.name AS 담당트레이너,
          COUNT(DISTINCT s.id) AS 누적수업수,
          COUNT(DISTINCT pa.id) AS 자세분석수,
          COUNT(DISTINCT a.id) AS 과제수,
          COUNT(DISTINCT CASE WHEN a.status = 'completed' OR ac.status = 'completed' THEN a.id END) AS 완료과제수,
          CASE
            WHEN COUNT(DISTINCT a.id) = 0 THEN 0
            ELSE ROUND(
              COUNT(DISTINCT CASE WHEN a.status = 'completed' OR ac.status = 'completed' THEN a.id END) * 100.0
              / COUNT(DISTINCT a.id),
              1
            )
          END AS 과제완료율,
          COUNT(DISTINCT r.id) AS 리포트수,
          COALESCE(MAX(s.session_date), '-') AS 최근이용일
        FROM members m
        JOIN trainers t ON m.trainer_id = t.id
        LEFT JOIN sessions s ON m.id = s.member_id
        LEFT JOIN posture_images pi ON m.id = pi.member_id
        LEFT JOIN posture_analysis pa ON pi.id = pa.posture_image_id
        LEFT JOIN assignments a ON m.id = a.member_id
        LEFT JOIN assignment_completions ac ON a.id = ac.assignment_id
        LEFT JOIN reports r ON m.id = r.member_id
        GROUP BY m.id, m.name, t.name
        ORDER BY 누적수업수 DESC, 자세분석수 DESC;
        """
    )


def service_activity_summary() -> pd.DataFrame:
    return query(
        """
        WITH dates AS (
          SELECT session_date AS activity_date FROM sessions
          UNION
          SELECT DATE(analyzed_at) AS activity_date FROM posture_analysis WHERE analyzed_at IS NOT NULL
          UNION
          SELECT DATE(created_at) AS activity_date FROM reports
        )
        SELECT
          d.activity_date AS 날짜,
          COUNT(DISTINCT s.id) AS 수업기록수,
          COUNT(DISTINCT pa.id) AS 자세분석수,
          COUNT(DISTINCT r.id) AS 리포트생성수
        FROM dates d
        LEFT JOIN sessions s ON s.session_date = d.activity_date
        LEFT JOIN posture_analysis pa ON DATE(pa.analyzed_at) = d.activity_date
        LEFT JOIN reports r ON DATE(r.created_at) = d.activity_date
        GROUP BY d.activity_date
        ORDER BY d.activity_date DESC;
        """
    )


def exercise_frequency_summary() -> pd.DataFrame:
    return query(
        """
        SELECT
          exercise_name AS 운동종목,
          COUNT(*) AS 기록횟수,
          COALESCE(ROUND(AVG(weight_kg), 1), '-') AS 평균중량,
          COALESCE(ROUND(AVG(sets), 1), '-') AS 평균세트,
          COALESCE(ROUND(AVG(reps), 1), '-') AS 평균횟수
        FROM session_exercises
        GROUP BY exercise_name
        ORDER BY 기록횟수 DESC, 운동종목 ASC;
        """
    )


def assignment_risk_summary() -> pd.DataFrame:
    return query(
        """
        SELECT
          m.name AS 회원,
          a.title AS 과제명,
          a.due_date AS 마감일,
          a.status AS 현재상태,
          COALESCE(ac.status, '-') AS 최근체크상태,
          CASE
            WHEN a.due_date < DATE('now', 'localtime')
             AND a.status != 'completed'
             AND COALESCE(ac.status, '') != 'completed'
            THEN '마감 지남'
            WHEN a.status = 'completed' OR ac.status = 'completed'
            THEN '완료'
            ELSE '진행 중'
          END AS 관리상태
        FROM assignments a
        JOIN members m ON a.member_id = m.id
        LEFT JOIN assignment_completions ac ON a.id = ac.assignment_id
        ORDER BY
          CASE 관리상태 WHEN '마감 지남' THEN 0 WHEN '진행 중' THEN 1 ELSE 2 END,
          a.due_date ASC;
        """
    )


def posture_quality_summary() -> pd.DataFrame:
    return query(
        """
        SELECT
          m.name AS 회원,
          pa.movement_name AS 동작,
          pa.model_name AS 모델명,
          pa.analysis_status AS 분석상태,
          COUNT(DISTINCT pk.id) AS Keypoint수,
          ps.total_score AS 총점,
          ps.knee_alignment_score AS 무릎정렬,
          ps.upper_body_score AS 상체,
          ps.pelvis_balance_score AS 골반,
          ps.lower_body_stability_score AS 하체안정성,
          ps.improvement_points AS 개선포인트,
          pa.analyzed_at AS 분석일시
        FROM posture_scores ps
        JOIN posture_analysis pa ON ps.analysis_id = pa.id
        JOIN posture_images pi ON pa.posture_image_id = pi.id
        JOIN members m ON pi.member_id = m.id
        LEFT JOIN posture_keypoints pk ON pa.id = pk.analysis_id
        GROUP BY
          m.name,
          pa.movement_name,
          pa.model_name,
          pa.analysis_status,
          ps.total_score,
          ps.knee_alignment_score,
          ps.upper_body_score,
          ps.pelvis_balance_score,
          ps.lower_body_stability_score,
          ps.improvement_points,
          pa.analyzed_at
        ORDER BY ps.total_score ASC, pa.analyzed_at DESC;
        """
    )


def service_admin_dashboard():
    return (
        render_admin_kpis(),
        trainer_usage_summary(),
        member_usage_summary(),
        service_activity_summary(),
        exercise_frequency_summary(),
        assignment_risk_summary(),
        posture_quality_summary(),
    )


def css() -> str:
    return """
.gradio-container { max-width: 1280px !important; }
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(140px, 1fr));
  gap: 10px;
  margin: 8px 0 16px;
}
.kpi-card {
  border: 1px solid #dbe3ef;
  border-radius: 8px;
  padding: 14px 16px;
  background: #ffffff;
}
.kpi-card span {
  display: block;
  color: #64748b;
  font-size: 13px;
  margin-bottom: 6px;
}
.kpi-card strong {
  font-size: 26px;
  color: #0f172a;
}
.kpi-card.warn strong { color: #b45309; }
.summary-card {
  border: 1px solid #dbe3ef;
  border-radius: 8px;
  padding: 16px 18px;
  background: #ffffff;
}
.summary-card h3 {
  margin: 0 0 12px;
  color: #0f172a;
}
.summary-card p {
  margin: 8px 0;
  color: #334155;
}
.mini-calendar {
  border: 1px solid #dbe3ef;
  border-radius: 8px;
  padding: 14px;
  background: #ffffff;
}
.calendar-title {
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 10px;
}
.mini-calendar table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
}
.mini-calendar th {
  color: #64748b;
  font-size: 12px;
  padding: 5px 0;
}
.mini-calendar td {
  border: 1px solid #e2e8f0;
  height: 30px;
  color: #334155;
}
.mini-calendar td.today {
  background: #0f172a;
  color: #ffffff;
  font-weight: 700;
}
"""


INITIAL_MEMBER = member_options()[0]
INITIAL_HOME = home_member_dashboard(INITIAL_MEMBER)
INITIAL_PROFILE = member_profile(INITIAL_MEMBER)
INITIAL_SESSIONS = session_options(INITIAL_MEMBER)
INITIAL_REPORTS = member_report(INITIAL_MEMBER)[0]
INITIAL_PORTAL = member_portal(INITIAL_MEMBER)
INITIAL_ADMIN = service_admin_dashboard()


with gr.Blocks(title="FitNote Trainer", css=css()) as demo:
    gr.Markdown(
        """
# FitNote Trainer
헬스트레이너를 위한 회원 관리, 수업 기록, 자세 분석, 과제, 리포트 프로토타입
"""
    )

    with gr.Tabs():
        with gr.Tab("홈 / 회원 대시보드"):
            home_member = gr.Dropdown(
                choices=member_options(),
                value=INITIAL_MEMBER,
                label="회원 검색/선택",
                filterable=True,
            )
            with gr.Row():
                home_calendar = gr.HTML(value=INITIAL_HOME[0], label="미니 달력")
                home_today_sessions = gr.Dataframe(value=INITIAL_HOME[1], label="오늘의 수업", interactive=False, wrap=True)
            home_memo = gr.Textbox(label="간단 메모", lines=2, placeholder="오늘 수업 전 확인할 내용을 적어두세요.")
            home_summary = gr.HTML(value=INITIAL_HOME[2], label="회원 요약 카드")
            with gr.Row():
                home_sessions = gr.Dataframe(value=INITIAL_HOME[3], label="최근 수업 기록", interactive=False, wrap=True)
                home_posture = gr.Dataframe(value=INITIAL_HOME[4], label="최근 자세 분석", interactive=False, wrap=True)
            home_assignments = gr.Dataframe(value=INITIAL_HOME[5], label="진행 중 과제", interactive=False, wrap=True)
            home_exercises = gr.CheckboxGroup(
                choices=today_exercise_options(INITIAL_MEMBER),
                value=[],
                label="오늘 세션에서 할 운동종목",
            )
            start_session_btn = gr.Button("체크 후 세션 시작", variant="primary")
            start_session_message = gr.Markdown()
            home_member.change(
                home_member_dashboard,
                inputs=home_member,
                outputs=[
                    home_calendar,
                    home_today_sessions,
                    home_summary,
                    home_sessions,
                    home_posture,
                    home_assignments,
                    home_exercises,
                ],
            )

        with gr.Tab("회원 등록 / 프로필"):
            with gr.Row():
                name_input = gr.Textbox(label="이름")
                phone_input = gr.Textbox(label="연락처")
                age_input = gr.Number(label="나이", precision=0)
                gender_input = gr.Dropdown(["남성", "여성", "기타"], label="성별")
            goal_input = gr.Textbox(label="운동 목표 입력", lines=2)
            experience_input = gr.Textbox(label="운동 경험 입력", lines=2)
            with gr.Row():
                inbody_input = gr.Image(label="인바디 프린트 이미지 업로드 (선택)", type="filepath")
                standing_posture_input = gr.Image(label="정자세 사진 업로드 (선택)", type="filepath")
                standing_skeleton_output = gr.Image(
                    label="정자세 YOLO 관절 포인트 / 스켈레톤",
                    type="filepath",
                    interactive=False,
                )
            standing_posture_status = gr.Markdown(
                value="**정자세 YOLO 상태:** 이미지를 업로드하면 관절 포인트와 스켈레톤을 표시합니다."
            )
            with gr.Row():
                analyze_standing_btn = gr.Button("정자세 YOLO 분석")
                redraw_standing_btn = gr.Button("수정 좌표로 다시 그리기")
            standing_keypoints_df = gr.Dataframe(
                value=keypoints_dataframe([]),
                headers=["keypoint_index", "point_name", "x", "y", "confidence"],
                datatype=["number", "str", "number", "number", "number"],
                label="정자세 관절 좌표 수정",
                interactive=True,
                wrap=True,
            )
            mobility_input = gr.Textbox(label="가동성 체크", lines=3, placeholder="예: 고관절 굴곡 제한, 발목 가동성 부족")
            with gr.Row():
                shoulder_asymmetry_input = gr.Checkbox(label="어깨 비대칭")
                pelvis_asymmetry_input = gr.Checkbox(label="골반 비대칭")
                other_asymmetry_input = gr.Textbox(label="기타 비대칭")
            with gr.Row():
                pain_input = gr.Textbox(label="통증 부위")
                injury_input = gr.Textbox(label="부상 이력")
            precautions_input = gr.Textbox(label="통증/주의사항 입력", lines=3)
            consent_input = gr.Checkbox(label="정보 수집 안내 동의")
            register_btn = gr.Button("회원 저장", variant="primary")
            register_message = gr.Markdown()

        with gr.Tab("수업 기록 / 자세 분석 / 과제"):
            session_member = gr.Dropdown(
                choices=member_options(),
                value=INITIAL_MEMBER,
                label="회원 선택",
                filterable=True,
            )
            with gr.Row():
                session_date_input = gr.Textbox(label="수업일", placeholder="예: 2026-07-02")
                focus_input = gr.Textbox(label="수업 정보 / 운동 부위", placeholder="예: 하체/코어")
                movement_input = gr.Textbox(label="자세 분석 동작", placeholder="예: 스쿼트")
            session_memo_input = gr.Textbox(label="세션 기록 작성", lines=4)
            voice_input = gr.Textbox(label="텍스트 기반 음성 메모", lines=4)
            voice_summary_output = gr.Markdown(label="음성 메모 요약")
            voice_ai_status = gr.Markdown(value="**AI 분석 상태:** 대기 중")
            summarize_btn = gr.Button("음성 메모 요약")
            with gr.Row():
                posture_image_input = gr.Image(label="자세 사진 업로드", type="filepath")
                posture_skeleton_output = gr.Image(
                    label="YOLO 관절 포인트 / 스켈레톤 결과",
                    type="filepath",
                    interactive=False,
                )
            posture_visual_status = gr.Markdown(
                value="**YOLO 시각화 상태:** 자세 이미지를 업로드하면 관절 포인트와 스켈레톤을 표시합니다."
            )
            trainer_feedback_input = gr.Textbox(label="트레이너 피드백 작성", lines=3)
            with gr.Row():
                assignment_title_input = gr.Textbox(label="과제명")
                assignment_target_input = gr.Textbox(label="목표량")
                assignment_due_input = gr.Textbox(label="마감일", placeholder="예: 2026-07-05")
            assignment_desc_input = gr.Textbox(label="과제 설명", lines=2)
            save_all_btn = gr.Button("전체 저장", variant="primary")
            save_all_message = gr.Markdown()
            with gr.Row():
                session_history_df = gr.Dataframe(value=INITIAL_PROFILE[1], label="선택 회원 수업 기록", interactive=False, wrap=True)
                session_posture_df = gr.Dataframe(value=posture_summary(), label="자세 분석 결과", interactive=False, wrap=True)
            session_assignment_df = gr.Dataframe(value=INITIAL_PROFILE[2], label="과제 목록", interactive=False, wrap=True)
            summarize_btn.click(
                summarize_voice_with_status,
                inputs=voice_input,
                outputs=[voice_summary_output, voice_ai_status],
            )
            session_member.change(
                lambda label: member_profile(label)[1],
                inputs=session_member,
                outputs=session_history_df,
            )
            session_member.change(
                lambda label: member_profile(label)[2],
                inputs=session_member,
                outputs=session_assignment_df,
            )

        with gr.Tab("회원 리포트"):
            report_member = gr.Dropdown(
                choices=member_options(),
                value=INITIAL_MEMBER,
                label="회원 선택",
                filterable=True,
            )
            report_session = gr.Dropdown(
                choices=INITIAL_SESSIONS,
                value=INITIAL_SESSIONS[0] if INITIAL_SESSIONS else None,
                label="세션 선택",
            )
            create_report_btn = gr.Button("리포트 생성", variant="primary")
            report_preview = gr.Markdown(label="생성 리포트")
            report_ai_status = gr.Markdown(value="**AI 분석 상태:** 대기 중")
            reports_df = gr.Dataframe(value=INITIAL_REPORTS, label="저장된 회원 리포트", interactive=False, wrap=True)
            report_member.change(update_session_dropdown, inputs=report_member, outputs=report_session)
            report_member.change(
                lambda label: member_report(label)[0],
                inputs=report_member,
                outputs=reports_df,
            )
            create_report_btn.click(
                generate_report,
                inputs=[report_member, report_session],
                outputs=[report_preview, report_ai_status, reports_df],
            )

        with gr.Tab("회원 전용 화면"):
            portal_member = gr.Dropdown(
                choices=member_options(),
                value=INITIAL_MEMBER,
                label="회원 선택",
                filterable=True,
            )
            portal_profile = gr.HTML(value=INITIAL_PORTAL[0], label="회원 프로필")
            with gr.Row():
                portal_assignments = gr.Dataframe(value=INITIAL_PORTAL[1], label="과제 확인", interactive=False, wrap=True)
                portal_schedule = gr.Dataframe(value=INITIAL_PORTAL[2], label="일정 확인", interactive=False, wrap=True)
            portal_history = gr.Dataframe(value=INITIAL_PORTAL[3], label="변화 기록 History", interactive=False, wrap=True)
            posture_score_df = gr.Dataframe(value=INITIAL_PORTAL[4], label="운동 자세별 점수 변화", interactive=False, wrap=True)
            weight_history_df = gr.Dataframe(value=INITIAL_PORTAL[5], label="몸무게 변화", interactive=False, wrap=True)
            portal_calendar = gr.HTML(value=INITIAL_PORTAL[6], label="회원 달력")
            portal_attendance = gr.Dataframe(value=INITIAL_PORTAL[7], label="출석/예약 기록", interactive=False, wrap=True)
            portal_member.change(
                member_portal,
                inputs=portal_member,
                outputs=[
                    portal_profile,
                    portal_assignments,
                    portal_schedule,
                    portal_history,
                    posture_score_df,
                    weight_history_df,
                    portal_calendar,
                    portal_attendance,
                ],
            )

        with gr.Tab("서비스 관리자"):
            admin_kpis = gr.HTML(value=INITIAL_ADMIN[0], label="서비스 전체 KPI")
            refresh_admin_btn = gr.Button("관리자 데이터 새로고침", variant="secondary")
            with gr.Row():
                trainer_usage_df = gr.Dataframe(value=INITIAL_ADMIN[1], label="트레이너별 사용량", interactive=False, wrap=True)
                member_usage_df = gr.Dataframe(value=INITIAL_ADMIN[2], label="회원별 사용량", interactive=False, wrap=True)
            service_activity_df = gr.Dataframe(value=INITIAL_ADMIN[3], label="날짜별 서비스 활성도", interactive=False, wrap=True)
            with gr.Row():
                exercise_frequency_df = gr.Dataframe(value=INITIAL_ADMIN[4], label="운동종목 기록 빈도", interactive=False, wrap=True)
                assignment_risk_df = gr.Dataframe(value=INITIAL_ADMIN[5], label="과제 완료/마감 관리", interactive=False, wrap=True)
            posture_quality_df = gr.Dataframe(value=INITIAL_ADMIN[6], label="낮은 자세 점수 및 개선 포인트", interactive=False, wrap=True)
            refresh_admin_btn.click(
                service_admin_dashboard,
                outputs=[
                    admin_kpis,
                    trainer_usage_df,
                    member_usage_df,
                    service_activity_df,
                    exercise_frequency_df,
                    assignment_risk_df,
                    posture_quality_df,
                ],
            )

        start_session_btn.click(
            start_session_from_home,
            inputs=[home_member, home_exercises, home_memo],
            outputs=[start_session_message, session_member, focus_input, session_memo_input],
        )

    register_btn.click(
        register_member,
        inputs=[
            name_input,
            phone_input,
            age_input,
            gender_input,
            goal_input,
            experience_input,
            inbody_input,
            standing_posture_input,
            mobility_input,
            shoulder_asymmetry_input,
            pelvis_asymmetry_input,
            other_asymmetry_input,
            pain_input,
            injury_input,
            precautions_input,
            consent_input,
        ],
        outputs=[register_message, home_member, session_member, report_member, report_session],
    )
    analyze_standing_btn.click(
        analyze_standing_posture_preview,
        inputs=standing_posture_input,
        outputs=[standing_skeleton_output, standing_posture_status, standing_keypoints_df],
    )
    redraw_standing_btn.click(
        redraw_standing_skeleton,
        inputs=[standing_posture_input, standing_keypoints_df],
        outputs=[standing_skeleton_output, standing_posture_status],
    )
    save_all_btn.click(
        save_training_flow,
        inputs=[
            session_member,
            session_date_input,
            focus_input,
            session_memo_input,
            voice_input,
            posture_image_input,
            movement_input,
            trainer_feedback_input,
            assignment_title_input,
            assignment_desc_input,
            assignment_target_input,
            assignment_due_input,
        ],
        outputs=[
            save_all_message,
            voice_summary_output,
            voice_ai_status,
            posture_skeleton_output,
            posture_visual_status,
            session_history_df,
            session_posture_df,
            session_assignment_df,
            report_session,
        ],
    )


if __name__ == "__main__":
    server_port = os.getenv("GRADIO_SERVER_PORT")
    demo.launch(
        server_name="127.0.0.1",
        server_port=int(server_port) if server_port else None,
        share=os.getenv("GRADIO_SHARE") == "1",
        show_api=False,
    )
