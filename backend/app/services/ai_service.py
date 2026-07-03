from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional


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


def _load_local_secrets() -> None:
    backend_root = Path(__file__).resolve().parents[2]
    project_root = backend_root.parent
    secret_paths = [
        project_root / "local_secrets.py",
        backend_root / "local_secrets.py",
    ]

    for secret_path in secret_paths:
        if not secret_path.exists():
            continue

        namespace: dict[str, Any] = {}
        try:
            exec(secret_path.read_text(encoding="utf-8"), namespace)
        except Exception:
            continue

        for key in ("OPENAI_API_KEY", "OPENAI_MODEL"):
            value = namespace.get(key)
            if value:
                os.environ.setdefault(key, str(value).strip())


_load_local_env()
_load_local_secrets()


def _openai_api_key() -> str:
    return os.getenv("OPENAI_API_KEY", "").strip()


def _openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"


def _openai_text(prompt: str) -> Optional[str]:
    api_key = _openai_api_key()
    if not api_key:
        return None

    try:
        from openai import OpenAI
    except Exception:
        return None

    try:
        client = OpenAI(api_key=api_key)
        model = _openai_model()
        if hasattr(client, "responses"):
            try:
                response = client.responses.create(model=model, input=prompt, temperature=0.2)
            except TypeError:
                response = client.responses.create(model=model, input=prompt)
            return getattr(response, "output_text", None)

        response = client.chat.completions.create(
            model=model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "너는 PT 수업 기록을 한국어로 간결하게 정리하는 assistant야."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
    except Exception:
        return None


def _whisper_model() -> str:
    return os.getenv("OPENAI_STT_MODEL", "whisper-1").strip() or "whisper-1"


def transcribe_audio(file_path: str) -> Optional[str]:
    """녹음 파일(mp3/mp4/webm/wav 등)을 OpenAI Whisper API로 텍스트 변환한다.

    다른 AI 기능과 달리 STT는 대체할 규칙 기반 fallback이 없다. API 키가
    없거나 호출이 실패하면 None을 반환하고, 호출부에서 "직접 입력" 흐름으로
    안내해야 한다.
    """
    api_key = _openai_api_key()
    if not api_key:
        return None
    if not Path(file_path).exists():
        return None

    try:
        from openai import OpenAI
    except Exception:
        return None

    try:
        client = OpenAI(api_key=api_key)
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model=_whisper_model(),
                file=audio_file,
                language="ko",
            )
        text = getattr(transcript, "text", None)
        return text.strip() if text else None
    except Exception:
        return None


def summarize_session_note(raw_text: str) -> Optional[dict[str, str]]:
    text = (raw_text or "").strip()
    if not text:
        return None

    prompt = f"""
아래 PT 수업 메모를 JSON으로 요약해줘.
반드시 아래 키만 사용해:
{{
  "exercise_summary": "...",
  "caution_note": "...",
  "assignment_candidate": "..."
}}

수업 메모:
{text}
""".strip()
    output = _openai_text(prompt)
    if not output:
        return None

    try:
        start = output.find("{")
        end = output.rfind("}")
        if start == -1 or end == -1:
            return None
        data: dict[str, Any] = json.loads(output[start : end + 1])
    except Exception:
        return None

    return {
        "exercise_summary": str(data.get("exercise_summary", "")).strip(),
        "caution_note": str(data.get("caution_note", "")).strip(),
        "assignment_candidate": str(data.get("assignment_candidate", "")).strip(),
    }


def generate_report_parts(
    member_name: str,
    session_date: str,
    workout_summary: str,
    posture_summary: str,
    trainer_feedback: str,
    caution_note: str,
    next_assignment: str,
) -> Optional[dict[str, str]]:
    prompt = f"""
PT 회원에게 전달할 수업 리포트 내용을 JSON으로 작성해줘.
의료 진단처럼 보이는 표현은 피하고, 운동 자세 참고와 과제 중심으로 작성해.

반드시 아래 JSON 키만 사용해:
{{
  "report_title": "...",
  "workout_summary": "...",
  "posture_summary": "...",
  "good_points": "...",
  "caution_points": "...",
  "next_assignment": "..."
}}

회원명: {member_name}
수업일: {session_date}
운동 기록: {workout_summary}
자세 분석: {posture_summary}
트레이너 피드백: {trainer_feedback}
주의사항: {caution_note}
다음 과제: {next_assignment}
""".strip()
    output = _openai_text(prompt)
    if not output:
        return None

    try:
        start = output.find("{")
        end = output.rfind("}")
        if start == -1 or end == -1:
            return None
        data: dict[str, Any] = json.loads(output[start : end + 1])
    except Exception:
        return None

    keys = [
        "report_title",
        "workout_summary",
        "posture_summary",
        "good_points",
        "caution_points",
        "next_assignment",
    ]
    return {key: str(data.get(key, "")).strip() for key in keys}
