"""비밀번호 해시 및 JWT 발급/검증 유틸리티.

데모/미니 프로젝트 수준의 인증이며, 실제 서비스 수준의 보안 강화(리프레시 토큰,
토큰 무효화 목록 등)는 범위 밖으로 둔다.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

SECRET_KEY = os.environ.get("FITNOTE_JWT_SECRET", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12  # 12시간

# passlib은 최신 bcrypt(>=4.1) 배포판과 버전 감지 호환성 문제가 있어
# bcrypt 패키지를 직접 사용한다.
_BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    pw_bytes = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    pw_bytes = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    try:
        return bcrypt.checkpw(pw_bytes, password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
