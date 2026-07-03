"""수업 기록 API (Tab 3 앞부분: 회원/수업정보, 세션기록, 음성메모 요약)."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from ..database import db_session
from ..deps import require_trainer
from ..schemas import (
    SessionCreate,
    SessionExerciseIn,
    SessionOut,
    SessionUpdate,
    VoiceSummaryOut,
    VoiceSummaryRequest,
)
from ..services.mock_ai import summarize_voice_memo

router = APIRouter(tags=["sessions"])


def _assert_member_owned(conn: sqlite3.Connection, member_id: int, trainer_id: int) -> None:
    row = conn.execute(
        "SELECT id FROM members WHERE id = ? AND trainer_id = ?", (member_id, trainer_id)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="회원을 찾을 수 없습니다")


def _get_owned_session(conn: sqlite3.Connection, session_id: int, trainer_id: int) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM sessions WHERE id = ? AND trainer_id = ?", (session_id, trainer_id)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="수업 기록을 찾을 수 없습니다")
    return row


def _session_out(conn: sqlite3.Connection, row: sqlite3.Row) -> SessionOut:
    ex_rows = conn.execute(
        "SELECT * FROM session_exercises WHERE session_id = ?", (row["id"],)
    ).fetchall()
    exercises = [
        SessionExerciseIn(
            exercise_name=r["exercise_name"],
            sets=r["sets"],
            reps=r["reps"],
            weight_kg=r["weight_kg"],
            note=r["note"],
        )
        for r in ex_rows
    ]
    return SessionOut(
        id=row["id"],
        member_id=row["member_id"],
        trainer_id=row["trainer_id"],
        session_date=row["session_date"],
        focus_area=row["focus_area"],
        memo=row["memo"],
        next_memo=row["next_memo"],
        raw_voice_text=row["raw_voice_text"],
        summary=row["summary"],
        created_at=row["created_at"],
        exercises=exercises,
    )


@router.post("/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    _assert_member_owned(conn, payload.member_id, trainer_id)

    cur = conn.execute(
        """
        INSERT INTO sessions
            (member_id, trainer_id, session_date, focus_area, memo, next_memo, raw_voice_text, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.member_id,
            trainer_id,
            payload.session_date,
            payload.focus_area,
            payload.memo,
            payload.next_memo,
            payload.raw_voice_text,
            payload.summary,
        ),
    )
    session_id = cur.lastrowid

    for ex in payload.exercises:
        conn.execute(
            """
            INSERT INTO session_exercises (session_id, exercise_name, sets, reps, weight_kg, note)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, ex.exercise_name, ex.sets, ex.reps, ex.weight_kg, ex.note),
        )
    conn.commit()

    row = _get_owned_session(conn, session_id, trainer_id)
    return _session_out(conn, row)


@router.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(
    session_id: int,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    row = _get_owned_session(conn, session_id, trainer_id)
    return _session_out(conn, row)


@router.put("/sessions/{session_id}", response_model=SessionOut)
def update_session(
    session_id: int,
    payload: SessionUpdate,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    _get_owned_session(conn, session_id, trainer_id)

    fields = payload.model_dump(exclude_unset=True)
    if fields:
        set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
        values = list(fields.values()) + [session_id]
        conn.execute(f"UPDATE sessions SET {set_clause} WHERE id = ?", values)
        conn.commit()

    row = _get_owned_session(conn, session_id, trainer_id)
    return _session_out(conn, row)


@router.get("/members/{member_id}/sessions", response_model=list[SessionOut])
def list_member_sessions(
    member_id: int,
    limit: int = 10,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    _assert_member_owned(conn, member_id, trainer_id)
    rows = conn.execute(
        "SELECT * FROM sessions WHERE member_id = ? ORDER BY session_date DESC, id DESC LIMIT ?",
        (member_id, limit),
    ).fetchall()
    return [_session_out(conn, r) for r in rows]


@router.post("/sessions/voice-summary", response_model=VoiceSummaryOut)
def voice_summary(
    payload: VoiceSummaryRequest,
    user: dict = Depends(require_trainer),
):
    result = summarize_voice_memo(payload.raw_text)
    return VoiceSummaryOut(**result)
