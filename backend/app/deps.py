"""공용 FastAPI 의존성: 로그인 쿠키에서 현재 사용자(role: trainer/member)를 확인한다."""

from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status

from . import security

COOKIE_NAME = "access_token"


def get_current_user(access_token: Optional[str] = Cookie(default=None)) -> dict:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인이 필요합니다")
    payload = security.decode_access_token(access_token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않거나 만료된 로그인입니다")
    return payload


def require_trainer(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "trainer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="트레이너 권한이 필요합니다")
    return user


def require_member(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "member":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="회원 권한이 필요합니다")
    return user
