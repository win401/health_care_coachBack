"""회원 등록/조회/수정 API (Tab 1 대시보드, Tab 2 회원 등록에 대응)."""

import sqlite3
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from ..database import db_session
from ..deps import require_trainer
from ..schemas import (
    HealthNoteIn,
    MemberCreate,
    MemberOut,
    MemberSummaryOut,
    MemberUpdate,
)

router = APIRouter(prefix="/members", tags=["members"])


def _row_to_member_out(row: sqlite3.Row) -> MemberOut:
    return MemberOut(
        id=row["id"],
        trainer_id=row["trainer_id"],
        name=row["name"],
        phone=row["phone"],
        age=row["age"],
        gender=row["gender"],
        fitness_goal=row["fitness_goal"],
        exercise_experience=row["exercise_experience"],
        status=row["status"],
        created_at=row["created_at"],
    )


def _get_owned_member(conn: sqlite3.Connection, member_id: int, trainer_id: int) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM members WHERE id = ? AND trainer_id = ?", (member_id, trainer_id)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="회원을 찾을 수 없습니다")
    return row


@router.post("", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def create_member(
    payload: MemberCreate,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    cur = conn.execute(
        """
        INSERT INTO members (trainer_id, name, phone, age, gender, fitness_goal, exercise_experience)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            trainer_id,
            payload.name,
            payload.phone,
            payload.age,
            payload.gender,
            payload.fitness_goal,
            payload.exercise_experience,
        ),
    )
    member_id = cur.lastrowid

    if payload.health_note is not None:
        note = payload.health_note
        conn.execute(
            """
            INSERT INTO member_health_notes (member_id, pain_area, injury_history, precautions, asymmetry_note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (member_id, note.pain_area, note.injury_history, note.precautions, note.asymmetry_note),
        )

    conn.execute(
        """
        INSERT INTO member_consents (member_id, consent_type, consent_text, is_agreed, agreed_at)
        VALUES (?, 'health_info_collection', '신체/건강 정보는 자세 분석 참고용으로만 사용합니다.', ?, CURRENT_TIMESTAMP)
        """,
        (member_id, 1 if payload.consent_agreed else 0),
    )
    conn.commit()

    row = _get_owned_member(conn, member_id, trainer_id)
    return _row_to_member_out(row)


@router.get("", response_model=list[MemberOut])
def list_members(
    q: Optional[str] = None,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    if q:
        rows = conn.execute(
            "SELECT * FROM members WHERE trainer_id = ? AND name LIKE ? ORDER BY created_at DESC",
            (trainer_id, f"%{q}%"),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM members WHERE trainer_id = ? ORDER BY created_at DESC", (trainer_id,)
        ).fetchall()
    return [_row_to_member_out(r) for r in rows]


@router.get("/{member_id}", response_model=MemberSummaryOut)
def get_member_summary(
    member_id: int,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    member_row = _get_owned_member(conn, member_id, trainer_id)

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


@router.put("/{member_id}", response_model=MemberOut)
def update_member(
    member_id: int,
    payload: MemberUpdate,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    _get_owned_member(conn, member_id, trainer_id)

    fields = payload.model_dump(exclude_unset=True)
    if fields:
        set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
        values = list(fields.values()) + [member_id]
        conn.execute(
            f"UPDATE members SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            values,
        )
        conn.commit()

    row = _get_owned_member(conn, member_id, trainer_id)
    return _row_to_member_out(row)


@router.put("/{member_id}/health-note")
def upsert_health_note(
    member_id: int,
    payload: HealthNoteIn,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    _get_owned_member(conn, member_id, trainer_id)
    conn.execute(
        """
        INSERT INTO member_health_notes (member_id, pain_area, injury_history, precautions, asymmetry_note)
        VALUES (?, ?, ?, ?, ?)
        """,
        (member_id, payload.pain_area, payload.injury_history, payload.precautions, payload.asymmetry_note),
    )
    conn.commit()
    return {"ok": True}
