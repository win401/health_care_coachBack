"""자세 사진 업로드 + YOLO optional 자세 분석 API (Tab 3 자세 분석 블록).

ultralytics/YOLO 모델을 사용할 수 있으면 keypoint를 추출하고, 실패하면
fallback 분석 결과를 저장한다.
"""

import sqlite3
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from ..database import db_session
from ..deps import require_trainer
from ..schemas import PostureAnalysisOut, PostureImageOut
from ..services.mock_ai import run_mock_posture_analysis

router = APIRouter(tags=["posture"])

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BACKEND_DIR / "uploads" / "posture"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _assert_member_owned(conn: sqlite3.Connection, member_id: int, trainer_id: int) -> None:
    row = conn.execute(
        "SELECT id FROM members WHERE id = ? AND trainer_id = ?", (member_id, trainer_id)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="회원을 찾을 수 없습니다")


def _image_with_analysis(conn: sqlite3.Connection, image_row: sqlite3.Row) -> PostureImageOut:
    analysis_row = conn.execute(
        "SELECT * FROM posture_analysis WHERE posture_image_id = ? ORDER BY id DESC LIMIT 1",
        (image_row["id"],),
    ).fetchone()

    analysis_out = None
    if analysis_row is not None:
        score_row = conn.execute(
            "SELECT * FROM posture_scores WHERE analysis_id = ? ORDER BY id DESC LIMIT 1",
            (analysis_row["id"],),
        ).fetchone()
        analysis_out = PostureAnalysisOut(
            id=analysis_row["id"],
            posture_image_id=analysis_row["posture_image_id"],
            model_name=analysis_row["model_name"],
            movement_name=analysis_row["movement_name"],
            analysis_status=analysis_row["analysis_status"],
            main_issue=analysis_row["main_issue"],
            sub_issue=analysis_row["sub_issue"],
            result_note=analysis_row["result_note"],
            analyzed_at=analysis_row["analyzed_at"],
            total_score=score_row["total_score"] if score_row else None,
            knee_alignment_score=score_row["knee_alignment_score"] if score_row else None,
            upper_body_score=score_row["upper_body_score"] if score_row else None,
            pelvis_balance_score=score_row["pelvis_balance_score"] if score_row else None,
            lower_body_stability_score=score_row["lower_body_stability_score"] if score_row else None,
            improvement_points=score_row["improvement_points"] if score_row else None,
        )

    return PostureImageOut(
        id=image_row["id"],
        member_id=image_row["member_id"],
        session_id=image_row["session_id"],
        movement_name=image_row["movement_name"],
        image_path=image_row["image_path"],
        upload_status=image_row["upload_status"],
        uploaded_at=image_row["uploaded_at"],
        analysis=analysis_out,
    )


@router.post("/posture/images", response_model=PostureImageOut, status_code=status.HTTP_201_CREATED)
def upload_posture_image(
    member_id: int = Form(...),
    session_id: Optional[int] = Form(default=None),
    movement_name: str = Form(default="스쿼트"),
    file: UploadFile = File(...),
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    _assert_member_owned(conn, member_id, trainer_id)

    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지 파일(jpg, jpeg, png, webp)만 업로드할 수 있습니다",
        )

    stored_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = UPLOAD_DIR / stored_name
    with dest_path.open("wb") as f:
        f.write(file.file.read())

    # DB에는 정적 파일 서빙 경로 기준으로 저장한다 (main.py에서 /uploads로 마운트)
    relative_path = f"/uploads/posture/{stored_name}"

    cur = conn.execute(
        """
        INSERT INTO posture_images (member_id, session_id, movement_name, image_path, upload_status)
        VALUES (?, ?, ?, ?, 'uploaded')
        """,
        (member_id, session_id, movement_name, relative_path),
    )
    conn.commit()

    row = conn.execute("SELECT * FROM posture_images WHERE id = ?", (cur.lastrowid,)).fetchone()
    return _image_with_analysis(conn, row)


@router.post("/posture/images/{image_id}/analyze", response_model=PostureImageOut)
def analyze_posture_image(
    image_id: int,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    image_row = conn.execute(
        """
        SELECT pi.* FROM posture_images pi
        JOIN members m ON m.id = pi.member_id
        WHERE pi.id = ? AND m.trainer_id = ?
        """,
        (image_id, trainer_id),
    ).fetchone()
    if image_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="자세 이미지를 찾을 수 없습니다")

    stored_path = BACKEND_DIR / str(image_row["image_path"]).lstrip("/")
    result = run_mock_posture_analysis(image_row["movement_name"] or "스쿼트", str(stored_path))

    cur = conn.execute(
        """
        INSERT INTO posture_analysis
            (posture_image_id, model_name, movement_name, analysis_status, main_issue, sub_issue, result_note, analyzed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (
            image_id,
            result["model_name"],
            result["movement_name"],
            result.get("analysis_status", "completed"),
            result["main_issue"],
            result["sub_issue"],
            result["result_note"],
        ),
    )
    analysis_id = cur.lastrowid

    for point in result.get("keypoints", []):
        conn.execute(
            """
            INSERT INTO posture_keypoints
                (analysis_id, keypoint_index, point_name, x, y, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
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

    conn.execute(
        """
        INSERT INTO posture_scores
            (analysis_id, total_score, knee_alignment_score, upper_body_score,
             pelvis_balance_score, lower_body_stability_score, improvement_points)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            analysis_id,
            result["total_score"],
            result["knee_alignment_score"],
            result["upper_body_score"],
            result["pelvis_balance_score"],
            result["lower_body_stability_score"],
            result["improvement_points"],
        ),
    )
    conn.execute(
        "UPDATE posture_images SET upload_status = 'analyzed' WHERE id = ?", (image_id,)
    )
    conn.commit()

    row = conn.execute("SELECT * FROM posture_images WHERE id = ?", (image_id,)).fetchone()
    return _image_with_analysis(conn, row)


@router.get("/members/{member_id}/posture", response_model=list[PostureImageOut])
def list_member_posture(
    member_id: int,
    limit: int = 10,
    user: dict = Depends(require_trainer),
    conn: sqlite3.Connection = Depends(db_session),
):
    trainer_id = int(user["sub"])
    _assert_member_owned(conn, member_id, trainer_id)
    rows = conn.execute(
        "SELECT * FROM posture_images WHERE member_id = ? ORDER BY uploaded_at DESC LIMIT ?",
        (member_id, limit),
    ).fetchall()
    return [_image_with_analysis(conn, r) for r in rows]
