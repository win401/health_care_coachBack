from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))


def _load_local_env() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_local_env()


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

COCO_SKELETON = [
    (5, 6),
    (5, 7),
    (7, 9),
    (6, 8),
    (8, 10),
    (5, 11),
    (6, 12),
    (11, 12),
    (11, 13),
    (13, 15),
    (12, 14),
    (14, 16),
    (0, 5),
    (0, 6),
]
KEYPOINT_CONFIDENCE_THRESHOLD = 0.2
MIN_CONFIDENT_KEYPOINTS = 6


@dataclass
class PoseAnalysisResult:
    model_name: str
    analysis_status: str
    main_issue: str
    sub_issue: str
    result_note: str
    total_score: int
    knee_alignment_score: int
    upper_body_score: int
    pelvis_balance_score: int
    lower_body_stability_score: int
    improvement_points: str
    keypoints: list[dict[str, float | int | str]]
    annotated_image_path: str | None = None


def _fallback_keypoints() -> list[dict[str, float | int | str]]:
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


def _fallback_result(movement_name: str, reason: str) -> PoseAnalysisResult:
    movement = movement_name or "자세 분석"
    return PoseAnalysisResult(
        model_name="fallback-rule-based",
        analysis_status="fallback",
        main_issue="무릎 정렬 확인 필요",
        sub_issue="상체 전방 기울어짐",
        result_note=f"{movement} 이미지 분석을 더미 규칙 기반으로 처리했습니다. 실제 YOLO 사용 불가 사유: {reason}",
        total_score=78,
        knee_alignment_score=72,
        upper_body_score=80,
        pelvis_balance_score=82,
        lower_body_stability_score=76,
        improvement_points="무릎이 안쪽으로 모이지 않도록 발끝 방향과 정렬을 확인",
        keypoints=_fallback_keypoints(),
        annotated_image_path=None,
    )


def _point_map(keypoints: list[dict[str, float | int | str]]) -> dict[str, dict[str, float | int | str]]:
    return {str(point["point_name"]): point for point in keypoints}


def _horizontal_distance(points: dict[str, dict[str, float | int | str]], left: str, right: str) -> float | None:
    if left not in points or right not in points:
        return None
    return abs(float(points[left]["x"]) - float(points[right]["x"]))


def _score_from_keypoints(keypoints: list[dict[str, float | int | str]]) -> dict[str, int | str]:
    points = _point_map(keypoints)
    shoulder_width = _horizontal_distance(points, "left_shoulder", "right_shoulder") or 1
    hip_width = _horizontal_distance(points, "left_hip", "right_hip") or shoulder_width
    knee_width = _horizontal_distance(points, "left_knee", "right_knee") or hip_width
    ankle_width = _horizontal_distance(points, "left_ankle", "right_ankle") or knee_width

    knee_delta = abs(knee_width - ankle_width) / max(ankle_width, 1)
    pelvis_delta = abs(shoulder_width - hip_width) / max(shoulder_width, 1)
    knee_score = max(45, min(95, round(92 - knee_delta * 80)))
    pelvis_score = max(50, min(95, round(90 - pelvis_delta * 60)))
    upper_score = 82 if pelvis_delta < 0.25 else 72
    lower_score = max(50, min(95, round((knee_score + pelvis_score) / 2)))
    total = round((knee_score + upper_score + pelvis_score + lower_score) / 4)

    if knee_score < 75:
        main_issue = "무릎 정렬 확인 필요"
        improvement = "무릎이 발끝 방향과 같은 방향을 향하도록 천천히 수행"
    elif pelvis_score < 75:
        main_issue = "골반 좌우 균형 확인 필요"
        improvement = "좌우 체중 분배와 골반 높이를 확인"
    else:
        main_issue = "전반적으로 안정적인 자세"
        improvement = "현재 정렬을 유지하며 반복 속도를 일정하게 조절"

    return {
        "total_score": total,
        "knee_alignment_score": knee_score,
        "upper_body_score": upper_score,
        "pelvis_balance_score": pelvis_score,
        "lower_body_stability_score": lower_score,
        "main_issue": main_issue,
        "improvement_points": improvement,
    }


def _extract_yolo_keypoints(result: Any) -> list[dict[str, float | int | str]]:
    if result.keypoints is None or len(result.keypoints) == 0:
        return []

    xy = result.keypoints.xy[0].cpu().numpy()
    conf = result.keypoints.conf[0].cpu().numpy() if result.keypoints.conf is not None else [0.0] * len(xy)
    keypoints: list[dict[str, float | int | str]] = []
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


def _confident_keypoint_count(keypoints: list[dict[str, float | int | str]]) -> int:
    return sum(1 for point in keypoints if float(point.get("confidence", 0)) >= KEYPOINT_CONFIDENCE_THRESHOLD)


def save_annotated_image(
    image_path: str,
    keypoints: list[dict[str, float | int | str]],
    suffix: str = "yolo_skeleton",
) -> str | None:
    if not keypoints:
        return None

    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return None

    try:
        source_path = Path(image_path)
        image = Image.open(source_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        width, height = image.size
        radius = max(4, round(min(width, height) * 0.008))
        line_width = max(3, round(min(width, height) * 0.006))
        font = ImageFont.load_default()
        point_by_index = {int(point["keypoint_index"]): point for point in keypoints}

        for start_index, end_index in COCO_SKELETON:
            start = point_by_index.get(start_index)
            end = point_by_index.get(end_index)
            if not start or not end:
                continue
            if (
                float(start.get("confidence", 0)) < KEYPOINT_CONFIDENCE_THRESHOLD
                or float(end.get("confidence", 0)) < KEYPOINT_CONFIDENCE_THRESHOLD
            ):
                continue
            draw.line(
                [
                    (float(start["x"]), float(start["y"])),
                    (float(end["x"]), float(end["y"])),
                ],
                fill=(0, 194, 255),
                width=line_width,
            )

        for point in keypoints:
            confidence = float(point.get("confidence", 0))
            if confidence < KEYPOINT_CONFIDENCE_THRESHOLD:
                continue
            x = float(point["x"])
            y = float(point["y"])
            index = int(point["keypoint_index"])
            fill = (255, 122, 24) if confidence >= 0.5 else (255, 205, 86)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill, outline=(255, 255, 255), width=2)
            draw.text((x + radius + 2, y - radius - 2), str(index), fill=(255, 255, 255), font=font)

        output_dir = ROOT / "backend" / "uploads" / "posture" / "annotated"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{source_path.stem}_{suffix}.png"
        image.save(output_path)
        return str(output_path)
    except Exception:
        return None


def analyze_pose(image_path: str | None, movement_name: str = "") -> PoseAnalysisResult:
    if not image_path:
        return _fallback_result(movement_name, "이미지 경로 없음")
    if not Path(image_path).exists():
        return _fallback_result(movement_name, "이미지 파일 없음")

    model_path = os.getenv("YOLO_POSE_MODEL", "yolov8n-pose.pt")
    try:
        from ultralytics import YOLO

        model = YOLO(model_path)
        results = model(image_path, verbose=False)
        if not results:
            return _fallback_result(movement_name, "YOLO 결과 없음")

        keypoints = _extract_yolo_keypoints(results[0])
        if not keypoints:
            return _fallback_result(movement_name, "사람 keypoint 미검출")
        confident_count = _confident_keypoint_count(keypoints)
        if confident_count < MIN_CONFIDENT_KEYPOINTS:
            return _fallback_result(movement_name, f"신뢰 가능한 keypoint 부족: {confident_count}개")

        scores = _score_from_keypoints(keypoints)
        annotated_image_path = save_annotated_image(image_path, keypoints)
        return PoseAnalysisResult(
            model_name=f"ultralytics:{model_path}",
            analysis_status="success",
            main_issue=str(scores["main_issue"]),
            sub_issue="자동 keypoint 기반 정렬 점검",
            result_note=f"{movement_name or '자세'} 이미지에서 {len(keypoints)}개 keypoint를 추출했습니다.",
            total_score=int(scores["total_score"]),
            knee_alignment_score=int(scores["knee_alignment_score"]),
            upper_body_score=int(scores["upper_body_score"]),
            pelvis_balance_score=int(scores["pelvis_balance_score"]),
            lower_body_stability_score=int(scores["lower_body_stability_score"]),
            improvement_points=str(scores["improvement_points"]),
            keypoints=keypoints,
            annotated_image_path=annotated_image_path,
        )
    except Exception as error:
        return _fallback_result(movement_name, str(error))
