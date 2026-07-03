"""회원 리포트 생성/조회 API (Tab 4 회원 리포트, Tab 5 회원 전용 화면에서 조회)."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from ..database import db_session
from ..deps import require_member, require_trainer
from ..schemas import ReportCreate, ReportOut
from ..services.ai_service import generate_report_parts

router = APIRouter(tags=["reports"])


def _row_to_out(row: sqlite3.Row) -> ReportOut:
    return ReportOut(
        id=row["id"],
        member_id=row["member_id"],
        session_id=row["session_id"],
        analysis_id=row["analysis_id"],
        report_title=row["report_title"],
        workout_summary=row["workout_summary"],
        posture_summary=row["posture_summary"],
        good_points=row["good_points"],
        caution_points=row["caution_points"],
        next_assignment=row["next_assignment"],
        created_at=row["created_at"],
    )


@router.post("/reports", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportCreate,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    member_row = conn.execute(
        "SELECT * FROM members WHERE id = ? AND trainer_id = ?", (payload.member_id, trainer_id)
    ).fetchone()
    if member_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="회원을 찾을 수 없습니다")

    # 세션: 지정 없으면 최근 세션
    if payload.session_id:
        session_row = conn.execute(
            "SELECT * FROM sessions WHERE id = ? AND member_id = ?",
            (payload.session_id, payload.member_id),
        ).fetchone()
    else:
        session_row = conn.execute(
            "SELECT * FROM sessions WHERE member_id = ? ORDER BY session_date DESC, id DESC LIMIT 1",
            (payload.member_id,),
        ).fetchone()

    exercises_text = "운동 기록 없음"
    if session_row is not None:
        ex_rows = conn.execute(
            "SELECT * FROM session_exercises WHERE session_id = ?", (session_row["id"],)
        ).fetchall()
        if ex_rows:
            exercises_text = ", ".join(
                f"{r['exercise_name']} {r['sets'] or '-'}세트 {r['reps'] or '-'}회" for r in ex_rows
            )
        elif session_row["summary"]:
            exercises_text = session_row["summary"]

    workout_summary = (
        f"{session_row['focus_area'] or '운동'} - {exercises_text}" if session_row else "세션 기록 없음"
    )

    # 자세 분석: 지정 없으면 최근 분석
    if payload.analysis_id:
        analysis_row = conn.execute(
            "SELECT * FROM posture_analysis WHERE id = ?", (payload.analysis_id,)
        ).fetchone()
    else:
        analysis_row = conn.execute(
            """
            SELECT pa.* FROM posture_analysis pa
            JOIN posture_images pi ON pi.id = pa.posture_image_id
            WHERE pi.member_id = ?
            ORDER BY pa.analyzed_at DESC, pa.id DESC LIMIT 1
            """,
            (payload.member_id,),
        ).fetchone()

    score_row = None
    if analysis_row is not None:
        score_row = conn.execute(
            "SELECT * FROM posture_scores WHERE analysis_id = ? ORDER BY id DESC LIMIT 1",
            (analysis_row["id"],),
        ).fetchone()

    if analysis_row is not None and score_row is not None:
        posture_summary = f"자세 점수 {score_row['total_score']}점 - {analysis_row['main_issue']}"
        good_points = "전반적인 운동 수행은 안정적입니다."
        caution_points = analysis_row["main_issue"] or "특이사항 없음"
    else:
        posture_summary = "자세 분석 결과 없음"
        good_points = "-"
        caution_points = "-"

    # 다음 과제: 진행중인 과제 목록
    assignment_rows = conn.execute(
        "SELECT title, target_amount FROM assignments WHERE member_id = ? AND status != 'completed' "
        "ORDER BY due_date IS NULL, due_date ASC LIMIT 5",
        (payload.member_id,),
    ).fetchall()
    next_assignment = (
        ", ".join(f"{r['title']}({r['target_amount']})" if r["target_amount"] else r["title"] for r in assignment_rows)
        if assignment_rows
        else "등록된 과제 없음"
    )

    session_date = session_row["session_date"] if session_row else ""
    ai_report = generate_report_parts(
        member_name=member_row["name"],
        session_date=session_date,
        workout_summary=workout_summary,
        posture_summary=posture_summary,
        trainer_feedback=good_points,
        caution_note=caution_points,
        next_assignment=next_assignment,
    )
    report_title = (
        payload.report_title
        or (ai_report["report_title"] if ai_report and ai_report.get("report_title") else None)
        or f"{member_row['name']} 회원 오늘의 PT 리포트"
    )
    if ai_report:
        workout_summary = ai_report.get("workout_summary") or workout_summary
        posture_summary = ai_report.get("posture_summary") or posture_summary
        good_points = ai_report.get("good_points") or good_points
        caution_points = ai_report.get("caution_points") or caution_points
        next_assignment = ai_report.get("next_assignment") or next_assignment

    cur = conn.execute(
        """
        INSERT INTO reports
            (member_id, session_id, analysis_id, report_title, workout_summary,
             posture_summary, good_points, caution_points, next_assignment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.member_id,
            session_row["id"] if session_row else None,
            analysis_row["id"] if analysis_row else None,
            report_title,
            workout_summary,
            posture_summary,
            good_points,
            caution_points,
            next_assignment,
        ),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (cur.lastrowid,)).fetchone()
    return _row_to_out(row)


@router.get("/reports/{report_id}", response_model=ReportOut)
def get_report(
    report_id: int,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    row = conn.execute(
        """
        SELECT r.* FROM reports r
        JOIN members m ON m.id = r.member_id
        WHERE r.id = ? AND m.trainer_id = ?
        """,
        (report_id, trainer_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="리포트를 찾을 수 없습니다")
    return _row_to_out(row)


@router.get("/members/{member_id}/reports", response_model=list[ReportOut])
def list_member_reports(
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
        "SELECT * FROM reports WHERE member_id = ? ORDER BY created_at DESC", (member_id,)
    ).fetchall()
    return [_row_to_out(r) for r in rows]


@router.get("/my/reports", response_model=list[ReportOut])
def list_my_reports(
    user: dict = Depends(require_member),
    conn: sqlite3.Connection = Depends(db_session),
):
    member_id = int(user["sub"])
    rows = conn.execute(
        "SELECT * FROM reports WHERE member_id = ? ORDER BY created_at DESC", (member_id,)
    ).fetchall()
    return [_row_to_out(r) for r in rows]
