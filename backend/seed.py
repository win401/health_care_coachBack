"""데모용 시드 데이터 스크립트.

실행:
    cd backend
    .venv/bin/python seed.py

기존 DB 파일(FITNOTE_DB_PATH, 기본값 ../fitnote_trainer.db)이 있으면 삭제하고 새로 만든다.
"""

import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import DB_PATH, get_connection, init_db  # noqa: E402
from app.security import hash_password  # noqa: E402
from app.services.mock_ai import run_mock_posture_analysis  # noqa: E402


def reset_db() -> None:
    db_path = Path(DB_PATH)
    if db_path.exists():
        db_path.unlink()
    init_db()


def seed() -> None:
    reset_db()
    conn = get_connection()

    # 트레이너 (데모 로그인: trainer1 / pass1234)
    cur = conn.execute(
        """
        INSERT INTO trainers (name, email, phone, center_name, login_id, password_hash)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            "김도현",
            "trainer@fitnote.demo",
            "010-1111-2222",
            "FitNote 강남점",
            "trainer1",
            hash_password("pass1234"),
        ),
    )
    trainer_id = cur.lastrowid

    members_data = [
        {
            "name": "박수진",
            "phone": "010-1234-5678",
            "age": 29,
            "gender": "F",
            "fitness_goal": "체중 감량, 자세 교정",
            "exercise_experience": "1년, 헬스 초보",
            "pain_area": "허리",
            "precautions": "무릎 정렬 주의",
            "asymmetry_note": "골반 비대칭",
        },
        {
            "name": "이민호",
            "phone": "010-2222-3333",
            "age": 34,
            "gender": "M",
            "fitness_goal": "근력 증가, 체력 향상",
            "exercise_experience": "3년차",
            "pain_area": "없음",
            "precautions": "없음",
            "asymmetry_note": "특이 비대칭 없음",
        },
        {
            "name": "최유나",
            "phone": "010-3333-4444",
            "age": 41,
            "gender": "F",
            "fitness_goal": "체형 교정, 통증 완화",
            "exercise_experience": "6개월",
            "pain_area": "어깨",
            "precautions": "어깨 가동범위 제한",
            "asymmetry_note": "어깨 비대칭",
        },
    ]

    for m in members_data:
        cur = conn.execute(
            """
            INSERT INTO members (trainer_id, name, phone, age, gender, fitness_goal, exercise_experience)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trainer_id,
                m["name"],
                m["phone"],
                m["age"],
                m["gender"],
                m["fitness_goal"],
                m["exercise_experience"],
            ),
        )
        member_id = cur.lastrowid

        conn.execute(
            """
            INSERT INTO member_health_notes (member_id, pain_area, injury_history, precautions, asymmetry_note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (member_id, m["pain_area"], None, m["precautions"], m["asymmetry_note"]),
        )
        conn.execute(
            """
            INSERT INTO member_consents (member_id, consent_type, consent_text, is_agreed, agreed_at)
            VALUES (?, 'health_info_collection', '신체/건강 정보는 자세 분석 참고용으로만 사용합니다.', 1, CURRENT_TIMESTAMP)
            """,
            (member_id,),
        )

        # 세션 1건
        cur = conn.execute(
            """
            INSERT INTO sessions
                (member_id, trainer_id, session_date, focus_area, memo, next_memo, raw_voice_text, summary)
            VALUES (?, ?, '2026-07-01', '하체', '스쿼트 위주로 진행', '다음 수업 때 자세 재확인', ?, ?)
            """,
            (
                member_id,
                trainer_id,
                f"오늘 {m['name']} 회원은 하체 운동을 진행했다. 무릎이 안쪽으로 모이는 경향이 있어 다음 수업 때 확인이 필요하다. 과제로 벽 스쿼트를 안내했다.",
                "하체 세션. 스쿼트 3세트 12회, 런지 2세트 10회 수행",
            ),
        )
        session_id = cur.lastrowid
        conn.execute(
            """
            INSERT INTO session_exercises (session_id, exercise_name, sets, reps, weight_kg, note)
            VALUES (?, '스쿼트', 3, 12, 40, NULL), (?, '런지', 2, 10, NULL, NULL)
            """,
            (session_id, session_id),
        )

        # 자세 이미지 + mock 분석
        cur = conn.execute(
            """
            INSERT INTO posture_images (member_id, session_id, movement_name, image_path, upload_status)
            VALUES (?, ?, '스쿼트', '/uploads/posture/demo-placeholder.jpg', 'analyzed')
            """,
            (member_id, session_id),
        )
        image_id = cur.lastrowid
        result = run_mock_posture_analysis("스쿼트")
        cur = conn.execute(
            """
            INSERT INTO posture_analysis
                (posture_image_id, model_name, movement_name, analysis_status, main_issue, sub_issue, result_note, analyzed_at)
            VALUES (?, ?, ?, 'completed', ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                image_id,
                result["model_name"],
                result["movement_name"],
                result["main_issue"],
                result["sub_issue"],
                result["result_note"],
            ),
        )
        analysis_id = cur.lastrowid
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

        # 피드백
        conn.execute(
            """
            INSERT INTO feedbacks (member_id, session_id, analysis_id, trainer_comment, caution_note, next_check_point)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                member_id,
                session_id,
                analysis_id,
                f"{result['improvement_points']}. 전반적으로 수행은 안정적이었습니다.",
                result["main_issue"],
                "다음 수업 때 무릎 정렬 재확인",
            ),
        )

        # 과제 2건
        conn.execute(
            """
            INSERT INTO assignments (member_id, session_id, title, description, target_amount, due_date, status)
            VALUES
                (?, ?, '벽 스쿼트', '무릎 정렬 개선 스트레칭', '20회', '2026-07-10', 'unchecked'),
                (?, ?, '고관절 스트레칭', '유연성 향상', '10분', '2026-07-10', 'unchecked')
            """,
            (member_id, session_id, member_id, session_id),
        )

        # 리포트 1건
        conn.execute(
            """
            INSERT INTO reports
                (member_id, session_id, analysis_id, report_title, workout_summary,
                 posture_summary, good_points, caution_points, next_assignment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                member_id,
                session_id,
                analysis_id,
                f"{m['name']} 회원 오늘의 PT 리포트",
                "하체 - 스쿼트 3세트 12회, 런지 2세트 10회",
                f"자세 점수 {result['total_score']}점 - {result['main_issue']}",
                "전반적인 운동 수행은 안정적입니다.",
                result["main_issue"],
                "벽 스쿼트 20회, 고관절 스트레칭 10분",
            ),
        )

    # 트레이너 오늘의 일정표 (Daily Schedule)
    today_str = date.today().isoformat()
    daily_tasks = [
        ("5:30", "Morning Routine", None),
        ("7:00", "Shower/Breakfast", None),
        ("9:00", "In-Person Training Session", "박수진 회원 하체 수업"),
        ("10:00", "Admin Work", "회원 리포트 정리"),
        ("13:00", "In-Person Training Session", "이민호 회원 근력 수업"),
        ("15:00", "In-Person Training Session", "최유나 회원 재활 수업"),
    ]
    for i, (time_label, title, notes) in enumerate(daily_tasks):
        conn.execute(
            """
            INSERT INTO trainer_daily_tasks (trainer_id, task_date, time_label, title, notes, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (trainer_id, today_str, time_label, title, notes, i),
        )

    conn.commit()
    conn.close()

    print("시드 데이터 생성 완료")
    print(f"DB 파일: {DB_PATH}")
    print("트레이너 로그인 -> 아이디: trainer1 / 비밀번호: pass1234")
    print("회원 로그인 예시 -> 이름: 박수진 / 전화번호 뒷자리: 5678")


if __name__ == "__main__":
    seed()
