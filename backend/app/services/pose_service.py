from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional, Union


COCO_KEYPOINTS = [
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
]


def _load_local_env() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_local_env()


def _fallback_keypoints() -> list[dict]:
    sample = [
        (5, "left_shoulder", 310.5, 188.2, 0.98),
        (6, "right_shoulder", 421.7, 190.4, 0.97),
        (11, "left_hip", 330.1, 360.8, 0.96),
        (12, "right_hip", 452.3, 365.6, 0.95),
        (13, "left_knee", 335.1, 510.8, 0.94),
        (14, "right_knee", 455.3, 515.6, 0.93),
        (15, "left_ankle", 330.4, 690.2, 0.91),
        (16, "right_ankle", 462.8, 692.1, 0.90),
    ]
    return [
        {
            "keypoint_index": index,
            "point_name": name,
            "x": x,
            "y": y,
            "confidence": confidence,
        }
        for index, name, x, y, confidence in sample
    ]


def _fallback_result(movement_name: str, reason: str) -> dict:
    return {
        "model_name": "fallback-rule-based",
        "movement_name": movement_name,
        "analysis_status": "fallback",
        "main_issue": "무릎 정렬 확인 필요",
        "sub_issue": "상체 전방 기울어짐",
        "result_note": f"실제 YOLO 사용 불가로 fallback 분석을 저장했습니다. 사유: {reason}",
        "total_score": 78,
        "knee_alignment_score": 72,
        "upper_body_score": 80,
        "pelvis_balance_score": 82,
        "lower_body_stability_score": 76,
        "improvement_points": "무릎이 안쪽으로 모이지 않도록 발끝 방향과 정렬을 확인",
        "keypoints": _fallback_keypoints(),
    }


def _point_map(keypoints: list[dict]) -> dict[str, dict]:
    return {str(point["point_name"]): point for point in keypoints}


def _distance(points: dict[str, dict], left: str, right: str) -> Optional[float]:
    if left not in points or right not in points:
        return None
    return abs(float(points[left]["x"]) - float(points[right]["x"]))


def _scores(keypoints: list[dict]) -> dict:
    points = _point_map(keypoints)
    shoulder_width = _distance(points, "left_shoulder", "right_shoulder") or 1
    hip_width = _distance(points, "left_hip", "right_hip") or shoulder_width
    knee_width = _distance(points, "left_knee", "right_knee") or hip_width
    ankle_width = _distance(points, "left_ankle", "right_ankle") or knee_width

    knee_delta = abs(knee_width - ankle_width) / max(ankle_width, 1)
    pelvis_delta = abs(shoulder_width - hip_width) / max(shoulder_width, 1)
    knee_score = max(45, min(95, round(92 - knee_delta * 80)))
    pelvis_score = max(50, min(95, round(90 - pelvis_delta * 60)))
    upper_score = 82 if pelvis_delta < 0.25 else 72
    lower_score = max(50, min(95, round((knee_score + pelvis_score) / 2)))
    total = round((knee_score + upper_score + pelvis_score + lower_score) / 4)

    if knee_score < 75:
        main_issue = "무릎 정렬 확인 필요"
        improvement_points = "무릎이 발끝 방향과 같은 방향을 향하도록 천천히 수행"
    elif pelvis_score < 75:
        main_issue = "골반 좌우 균형 확인 필요"
        improvement_points = "좌우 체중 분배와 골반 높이를 확인"
    else:
        main_issue = "전반적으로 안정적인 자세"
        improvement_points = "현재 정렬을 유지하며 반복 속도를 일정하게 조절"

    return {
        "total_score": total,
        "knee_alignment_score": knee_score,
        "upper_body_score": upper_score,
        "pelvis_balance_score": pelvis_score,
        "lower_body_stability_score": lower_score,
        "main_issue": main_issue,
        "improvement_points": improvement_points,
    }


def _extract_yolo_keypoints(result: Any) -> list[dict]:
    if result.keypoints is None or len(result.keypoints) == 0:
        return []

    xy = result.keypoints.xy[0].cpu().numpy()
    conf = result.keypoints.conf[0].cpu().numpy() if result.keypoints.conf is not None else [0.0] * len(xy)
    keypoints = []
    for index, point in enumerate(xy):
        if index >= len(COCO_KEYPOINTS):
            break
        keypoints.append(
            {
                "keypoint_index": index,
                "point_name": COCO_KEYPOINTS[index],
                "x": round(float(point[0]), 3),
                "y": round(float(point[1]), 3),
                "confidence": round(float(conf[index]), 4),
            }
        )
    return keypoints


def analyze_pose(image_path: Optional[Union[str, Path]], movement_name: str = "스쿼트") -> dict:
    if image_path is None:
        return _fallback_result(movement_name, "이미지 경로 없음")

    path = Path(image_path)
    if not path.exists():
        return _fallback_result(movement_name, "이미지 파일 없음")

    model_path = os.getenv("YOLO_POSE_MODEL", "yolov8n-pose.pt")
    try:
        from ultralytics import YOLO

        model = YOLO(model_path)
        results = model(str(path), verbose=False)
        if not results:
            return _fallback_result(movement_name, "YOLO 결과 없음")

        keypoints = _extract_yolo_keypoints(results[0])
        if not keypoints:
            return _fallback_result(movement_name, "사람 keypoint 미검출")

        scores = _scores(keypoints)
        return {
            "model_name": f"ultralytics:{model_path}",
            "movement_name": movement_name,
            "analysis_status": "success",
            "main_issue": scores["main_issue"],
            "sub_issue": "자동 keypoint 기반 정렬 점검",
            "result_note": f"{movement_name} 이미지에서 {len(keypoints)}개 keypoint를 추출했습니다.",
            "total_score": scores["total_score"],
            "knee_alignment_score": scores["knee_alignment_score"],
            "upper_body_score": scores["upper_body_score"],
            "pelvis_balance_score": scores["pelvis_balance_score"],
            "lower_body_stability_score": scores["lower_body_stability_score"],
            "improvement_points": scores["improvement_points"],
            "keypoints": keypoints,
        }
    except Exception as error:
        return _fallback_result(movement_name, str(error))
