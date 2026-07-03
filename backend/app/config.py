"""공용 경로 설정.

배포 환경(Railway 등)에서는 FITNOTE_UPLOAD_DIR 환경변수로 영구 볼륨 경로를
지정한다(예: /data/uploads). 지정하지 않으면 로컬 개발 기본값인
backend/uploads를 그대로 사용한다.
"""

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

UPLOAD_ROOT = Path(os.environ.get("FITNOTE_UPLOAD_DIR", str(BACKEND_DIR / "uploads")))
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
