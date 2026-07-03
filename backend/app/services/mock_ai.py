from __future__ import annotations

"""AI/YOLO optional 서비스와 규칙 기반 fallback 로직.

OPENAI_API_KEY 또는 YOLO 실행 환경이 없으면 기존 demo-rule-based 결과로 안전하게
fallback한다.
"""

import random
from typing import Optional

from .ai_service import summarize_session_note
from .pose_service import analyze_pose

CAUTION_KEYWORDS = ["통증", "무릎", "허리", "어깨", "불편", "주의"]
ASSIGNMENT_KEYWORDS = ["숙제", "과제", "집에서", "스트레칭", "다음"]


def summarize_voice_memo(raw_text: str) -> dict:
    text = (raw_text or "").strip()
    if not text:
        return {
            "exercise_summary": "입력된 음성 메모가 없습니다.",
            "caution_note": "특이 통증 언급 없음",
            "assignment_candidate": "별도 과제 언급 없음",
        }

    ai_result = summarize_session_note(text)
    if ai_result and all(ai_result.values()):
        return ai_result

    cautions = [w for w in CAUTION_KEYWORDS if w in text]
    assignments = [w for w in ASSIGNMENT_KEYWORDS if w in text]

    return {
        "exercise_summary": text[:120] + ("..." if len(text) > 120 else ""),
        "caution_note": ", ".join(cautions) if cautions else "특이 통증 언급 없음",
        "assignment_candidate": (
            "홈트레이닝/스트레칭 과제 후보 있음" if assignments else "별도 과제 언급 없음"
        ),
    }


_MOCK_ISSUE_POOL = [
    {
        "main_issue": "무릎이 안쪽으로 모이는 경향",
        "sub_issue": "상체가 기준보다 앞으로 기울어짐",
        "improvement_points": "무릎이 발끝 방향과 같은 방향을 향하도록 벽 스쿼트 연습",
        "knee": 68,
        "upper": 78,
        "pelvis": 74,
        "lower": 70,
    },
    {
        "main_issue": "골반이 한쪽으로 기울어짐",
        "sub_issue": "허리 과신전 경향",
        "improvement_points": "코어 안정화 운동과 골반 정렬 스트레칭 추가",
        "knee": 80,
        "upper": 72,
        "pelvis": 65,
        "lower": 75,
    },
    {
        "main_issue": "특이 문제 없음, 자세 양호",
        "sub_issue": "경미한 발목 가동성 제한",
        "improvement_points": "발목 가동성 향상을 위한 카프 스트레칭 권장",
        "knee": 88,
        "upper": 90,
        "pelvis": 86,
        "lower": 84,
    },
]


def run_mock_posture_analysis(movement_name: str, image_path: Optional[str] = None) -> dict:
    """YOLO pose 분석을 우선 시도하고 실패하면 demo-rule-based 결과를 반환한다."""
    if image_path:
        return analyze_pose(image_path, movement_name)

    issue = random.choice(_MOCK_ISSUE_POOL)
    total = round((issue["knee"] + issue["upper"] + issue["pelvis"] + issue["lower"]) / 4)
    return {
        "model_name": "demo-rule-based",
        "movement_name": movement_name,
        "analysis_status": "fallback",
        "main_issue": issue["main_issue"],
        "sub_issue": issue["sub_issue"],
        "result_note": "이 결과는 의료 진단이 아니라 운동 자세 참고 자료입니다.",
        "total_score": total,
        "knee_alignment_score": issue["knee"],
        "upper_body_score": issue["upper"],
        "pelvis_balance_score": issue["pelvis"],
        "lower_body_stability_score": issue["lower"],
        "improvement_points": issue["improvement_points"],
        "keypoints": [],
    }
