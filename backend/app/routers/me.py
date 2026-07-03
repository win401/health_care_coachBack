"""회원 본인(member) 전용 조회 API (Tab 5 회원 전용 화면)."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from ..database import db_session
from ..deps import require_member
from ..schemas import AssignmentOut, MemberOut, MemberSummaryOut
from .assignments import _row_to_out as _assignment_to_out
from .members import _row_to_member_out
from .sessions import _session_out

router = APIRouter(prefix="/my", tags=["me"])


@router.get("/profile", response_model=MemberSummaryOut)
def my_profile(
    user: dict = Depends(require_member),
    conn: sqlite3.Connection = Depends(db_session),
):
    member_id = int(user["sub"])
    member_row = conn.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()

    health_note = conn.execute(
        "SELECT * FROM member_health_notes WHERE member_id = ? ORDER BY created_at DESC LIMIT 1",
        (member_id,),
    ).fetchone()
    last_session = conn.execute(
        "SELECT * FROM sessions WHERE member_id = ? ORDER BY session_date DESC, id DESC LIMIT 1",
        (member_id,),
    ).fetchone()
    last_score = conn.execute(
        """
        SELECT ps.total_score, pa.main_issue
        FROM posture_scores ps
        JOIN posture_analysis pa ON pa.id = ps.analysis_id
        JOIN posture_images pi ON pi.id = pa.posture_image_id
        WHERE pi.member_id = ?
        ORDER BY ps.created_at DESC, ps.id DESC LIMIT 1
        """,
        (member_id,),
    ).fetchone()
    open_count_row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM assignments WHERE member_id = ? AND status != 'completed'",
        (member_id,),
    ).fetchone()

    return MemberSummaryOut(
        member=_row_to_member_out(member_row),
        pain_area=health_note["pain_area"] if health_note else None,
        precautions=health_note["precautions"] if health_note else None,
        injury_history=health_note["injury_history"] if health_note else None,
        last_session_date=last_session["session_date"] if last_session else None,
        last_session_focus=last_session["focus_area"] if last_session else None,
        last_posture_score=last_score["total_score"] if last_score else None,
        last_posture_main_issue=last_score["main_issue"] if last_score else None,
        open_assignment_count=open_count_row["cnt"],
    )


@router.get("/sessions")
def my_sessions(
    limit: int = 10,
    user: dict = Depends(require_member),
    conn: sqlite3.Connection = Depends(db_session),
):
    member_id = int(user["sub"])
    rows = conn.execute(
        "SELECT * FROM sessions WHERE member_id = ? ORDER BY session_date DESC, id DESC LIMIT ?",
        (member_id, limit),
    ).fetchall()
    return [_session_out(conn, r) for r in rows]


@router.get("/posture-history")
def my_posture_history(
    limit: int = 20,
    user: dict = Depends(require_member),
    conn: sqlite3.Connection = Depends(db_session),
):
    member_id = int(user["sub"])
    rows = conn.execute(
        """
        SELECT pa.analyzed_at, ps.total_score, ps.knee_alignment_score, ps.upper_body_score,
               ps.pelvis_balance_score, ps.lower_body_stability_score, pa.main_issue
        FROM posture_scores ps
        JOIN posture_analysis pa ON pa.id = ps.analysis_id
        JOIN posture_images pi ON pi.id = pa.posture_image_id
        WHERE pi.member_id = ?
        ORDER BY pa.analyzed_at ASC
        LIMIT ?
        """,
        (member_id, limit),
    ).fetchall()
    return [dict(r) for r in rows]


@router.put("/assignments/{assignment_id}", response_model=AssignmentOut)
def update_my_assignment_status(
    assignment_id: int,
    status_value: str,
    user: dict = Depends(require_member),
    conn: sqlite3.Connection = Depends(db_session),
):
    member_id = int(user["sub"])
    row = conn.execute(
        "SELECT * FROM assignments WHERE id = ? AND member_id = ?", (assignment_id, member_id)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="과제를 찾을 수 없습니다")

    if status_value not in ("unchecked", "in_progress", "completed"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="올바르지 않은 상태값입니다")

    if status_value == "completed":
        conn.execute(
            "UPDATE assignments SET status = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status_value, assignment_id),
        )
    else:
        conn.execute("UPDATE assignments SET status = ? WHERE id = ?", (status_value, assignment_id))
    conn.commit()

    row = conn.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,)).fetchone()
    return _assignment_to_out(row)


@router.get("/body-profile")
def my_body_profile(
    user: dict = Depends(require_member),
    conn: sqlite3.Connection = Depends(db_session),
):
    member_id = int(user["sub"])
    rows = conn.execute(
        "SELECT height_cm, weight_kg, created_at FROM member_body_profiles WHERE member_id = ? ORDER BY created_at ASC",
        (member_id,),
    ).fetchall()
    return [dict(r) for r in rows]
