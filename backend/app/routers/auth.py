"""로그인 API.

- 트레이너: login_id + password (bcrypt 검증)
- 회원: 이름 + 전화번호 뒷 4자리 (비밀번호 없음, 간단 본인확인 수준)

둘 다 성공 시 동일한 형태의 JWT를 httpOnly 쿠키(access_token)에 담아 내려준다.
"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Response, status

from .. import security
from ..database import db_session
from ..deps import COOKIE_NAME, get_current_user
from ..schemas import AuthUserOut, MemberLoginRequest, TrainerLoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_MAX_AGE_SECONDS = 60 * 60 * 12  # 12시간


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=COOKIE_MAX_AGE_SECONDS,
        path="/",
    )


@router.post("/trainer/login", response_model=AuthUserOut)
def trainer_login(
    payload: TrainerLoginRequest,
    response: Response,
    conn: sqlite3.Connection = Depends(db_session),
):
    row = conn.execute(
        "SELECT id, name, password_hash FROM trainers WHERE login_id = ?",
        (payload.login_id,),
    ).fetchone()
    if row is None or not security.verify_password(payload.password, row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다",
        )
    token = security.create_access_token(
        {"sub": str(row["id"]), "role": "trainer", "name": row["name"]}
    )
    _set_auth_cookie(response, token)
    return AuthUserOut(id=row["id"], name=row["name"], role="trainer")


@router.post("/member/login", response_model=AuthUserOut)
def member_login(
    payload: MemberLoginRequest,
    response: Response,
    conn: sqlite3.Connection = Depends(db_session),
):
    if not payload.phone_last4.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="전화번호 뒷자리 4자리 숫자를 입력해주세요",
        )
    rows = conn.execute(
        "SELECT id, name, phone FROM members WHERE name = ?", (payload.name,)
    ).fetchall()
    matched = None
    for row in rows:
        phone_digits = "".join(ch for ch in (row["phone"] or "") if ch.isdigit())
        if phone_digits.endswith(payload.phone_last4):
            matched = row
            break
    if matched is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이름 또는 전화번호가 일치하지 않습니다",
        )
    token = security.create_access_token(
        {"sub": str(matched["id"]), "role": "member", "name": matched["name"]}
    )
    _set_auth_cookie(response, token)
    return AuthUserOut(id=matched["id"], name=matched["name"], role="member")


@router.get("/me", response_model=AuthUserOut)
def me(user: dict = Depends(get_current_user)):
    return AuthUserOut(id=int(user["sub"]), name=user.get("name", ""), role=user.get("role", ""))


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}
