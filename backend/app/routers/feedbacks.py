"""트레이너 피드백 API (Tab 3 트레이너 피드백 블록)."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from ..database import db_session
from ..deps import require_trainer
from ..schemas import FeedbackCreate, FeedbackOut

router = APIRouter(tags=["feedbacks"])


def _row_to_out(row: sqlite3.Row) -> FeedbackOut:
    return FeedbackOut(
        id=row["id"],
        member_id=row["member_id"],
        session_id=row["session_id"],
        analysis_id=row["analysis_id"],
        trainer_comment=row["trainer_comment"],
        caution_note=row["caution_note"],
        next_check_point=row["next_check_point"],
        created_at=row["created_at"],
    )


@router.post("/feedbacks", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: FeedbackCreate,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    member_row = conn.execute(
        "SELECT id FROM members WHERE id = ? AND trainer_id = ?", (payload.member_id, trainer_id)
    ).fetchone()
    if member_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="회원을 찾을 수 없습니다")

    cur = conn.execute(
        """
        INSERT INTO feedbacks (member_id, session_id, analysis_id, trainer_comment, caution_note, next_check_point)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            payload.member_id,
            payload.session_id,
            payload.analysis_id,
            payload.trainer_comment,
            payload.caution_note,
            payload.next_check_point,
        ),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM feedbacks WHERE id = ?", (cur.lastrowid,)).fetchone()
    return _row_to_out(row)


@router.get("/members/{member_id}/feedbacks", response_model=list[FeedbackOut])
def list_member_feedbacks(
    member_id: int,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    member_row = conn.execute(
        "SELECT id FROM members WHERE id = ? AND trainer_id = ?", (member_id, trainer_id)
    ).fetchone()
    if member_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="회원을 찾을 수 없습니다")
    rows = conn.execute(
        "SELECT * FROM feedbacks WHERE member_id = ? ORDER BY created_at DESC", (member_id,)
    ).fetchall()
    return [_row_to_out(r) for r in rows]
