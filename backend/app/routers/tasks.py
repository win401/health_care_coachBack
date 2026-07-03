"""트레이너 개인 일정표 API (대시보드 Daily Schedule 표).

회원과 무관한, 트레이너 본인의 하루 일정(수업/행정업무 등)을 관리한다.
"""

import sqlite3
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from ..database import db_session
from ..deps import require_trainer
from ..schemas import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _row_to_out(row: sqlite3.Row) -> TaskOut:
    return TaskOut(
        id=row["id"],
        trainer_id=row["trainer_id"],
        task_date=row["task_date"],
        time_label=row["time_label"],
        title=row["title"],
        notes=row["notes"],
        is_done=bool(row["is_done"]),
        sort_order=row["sort_order"],
        created_at=row["created_at"],
    )


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    max_order_row = conn.execute(
        "SELECT COALESCE(MAX(sort_order), -1) AS max_order FROM trainer_daily_tasks WHERE trainer_id = ? AND task_date = ?",
        (trainer_id, payload.task_date),
    ).fetchone()
    next_order = max_order_row["max_order"] + 1

    cur = conn.execute(
        """
        INSERT INTO trainer_daily_tasks (trainer_id, task_date, time_label, title, notes, sort_order)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (trainer_id, payload.task_date, payload.time_label, payload.title, payload.notes, next_order),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM trainer_daily_tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
    return _row_to_out(row)


@router.get("", response_model=list[TaskOut])
def list_tasks(
    period: str = "today",
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    today = date.today()

    if period == "today":
        rows = conn.execute(
            """
            SELECT * FROM trainer_daily_tasks
            WHERE trainer_id = ? AND task_date = ?
            ORDER BY sort_order ASC, id ASC
            """,
            (trainer_id, today.isoformat()),
        ).fetchall()
    elif period == "week":
        start = today - timedelta(days=today.weekday())  # 이번 주 월요일
        end = start + timedelta(days=6)  # 이번 주 일요일
        rows = conn.execute(
            """
            SELECT * FROM trainer_daily_tasks
            WHERE trainer_id = ? AND task_date BETWEEN ? AND ?
            ORDER BY task_date ASC, sort_order ASC, id ASC
            """,
            (trainer_id, start.isoformat(), end.isoformat()),
        ).fetchall()
    elif period == "all":
        rows = conn.execute(
            """
            SELECT * FROM trainer_daily_tasks
            WHERE trainer_id = ?
            ORDER BY task_date ASC, sort_order ASC, id ASC
            """,
            (trainer_id,),
        ).fetchall()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="period는 today|week|all 중 하나여야 합니다")

    return [_row_to_out(r) for r in rows]


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    existing = conn.execute(
        "SELECT * FROM trainer_daily_tasks WHERE id = ? AND trainer_id = ?", (task_id, trainer_id)
    ).fetchone()
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일정을 찾을 수 없습니다")

    fields = payload.model_dump(exclude_unset=True)
    if "is_done" in fields:
        fields["is_done"] = 1 if fields["is_done"] else 0
    if fields:
        set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
        values = list(fields.values()) + [task_id]
        conn.execute(f"UPDATE trainer_daily_tasks SET {set_clause} WHERE id = ?", values)
        conn.commit()

    row = conn.execute("SELECT * FROM trainer_daily_tasks WHERE id = ?", (task_id,)).fetchone()
    return _row_to_out(row)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    existing = conn.execute(
        "SELECT id FROM trainer_daily_tasks WHERE id = ? AND trainer_id = ?", (task_id, trainer_id)
    ).fetchone()
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일정을 찾을 수 없습니다")
    conn.execute("DELETE FROM trainer_daily_tasks WHERE id = ?", (task_id,))
    conn.commit()
    return None
