"""과제 등록/조회/상태변경 API (Tab 3 과제 등록, Tab 5 회원 전용 화면에서 조회)."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from ..database import db_session
from ..deps import require_member, require_trainer
from ..schemas import AssignmentCreate, AssignmentOut, AssignmentUpdate

router = APIRouter(tags=["assignments"])


def _row_to_out(row: sqlite3.Row) -> AssignmentOut:
    return AssignmentOut(
        id=row["id"],
        member_id=row["member_id"],
        session_id=row["session_id"],
        title=row["title"],
        description=row["description"],
        target_amount=row["target_amount"],
        due_date=row["due_date"],
        status=row["status"],
        created_at=row["created_at"],
        completed_at=row["completed_at"],
    )


def _assert_member_owned(conn: sqlite3.Connection, member_id: int, trainer_id: int) -> None:
    row = conn.execute(
        "SELECT id FROM members WHERE id = ? AND trainer_id = ?", (member_id, trainer_id)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="회원을 찾을 수 없습니다")


@router.post("/assignments", response_model=AssignmentOut, status_code=status.HTTP_201_CREATED)
def create_assignment(
    payload: AssignmentCreate,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    _assert_member_owned(conn, payload.member_id, trainer_id)

    cur = conn.execute(
        """
        INSERT INTO assignments (member_id, session_id, title, description, target_amount, due_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.member_id,
            payload.session_id,
            payload.title,
            payload.description,
            payload.target_amount,
            payload.due_date,
            payload.status,
        ),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM assignments WHERE id = ?", (cur.lastrowid,)).fetchone()
    return _row_to_out(row)


@router.get("/members/{member_id}/assignments", response_model=list[AssignmentOut])
def list_member_assignments_for_trainer(
    member_id: int,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    _assert_member_owned(conn, member_id, trainer_id)
    rows = conn.execute(
        "SELECT * FROM assignments WHERE member_id = ? ORDER BY due_date IS NULL, due_date ASC",
        (member_id,),
    ).fetchall()
    return [_row_to_out(r) for r in rows]


@router.put("/assignments/{assignment_id}", response_model=AssignmentOut)
def update_assignment(
    assignment_id: int,
    payload: AssignmentUpdate,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    row = conn.execute(
        """
        SELECT a.* FROM assignments a
        JOIN members m ON m.id = a.member_id
        WHERE a.id = ? AND m.trainer_id = ?
        """,
        (assignment_id, trainer_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="과제를 찾을 수 없습니다")

    fields = payload.model_dump(exclude_unset=True)
    if fields:
        if fields.get("status") == "completed":
            fields["completed_at"] = None  # placeholder, set below via SQL CURRENT_TIMESTAMP
        set_parts = []
        values = []
        for k, v in fields.items():
            if k == "completed_at":
                set_parts.append("completed_at = CURRENT_TIMESTAMP")
            else:
                set_parts.append(f"{k} = ?")
                values.append(v)
        values.append(assignment_id)
        conn.execute(f"UPDATE assignments SET {', '.join(set_parts)} WHERE id = ?", values)
        conn.commit()

    row = conn.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,)).fetchone()
    return _row_to_out(row)


@router.get("/my/assignments", response_model=list[AssignmentOut])
def list_my_assignments(
    user: dict = Depends(require_member),
    conn: sqlite3.Connection = Depends(db_session),
):
    member_id = int(user["sub"])
    rows = conn.execute(
        "SELECT * FROM assignments WHERE member_id = ? ORDER BY due_date IS NULL, due_date ASC",
        (member_id,),
    ).fetchall()
    return [_row_to_out(r) for r in rows]
