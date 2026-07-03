import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import UPLOAD_ROOT
from .database import init_db
from .routers import assignments, auth, feedbacks, me, members, posture, reports, sessions, tasks

app = FastAPI(title="FitNote Trainer API")

# 배포 환경에서는 CORS_ORIGINS 환경변수(콤마로 구분)로 Vercel 등 실제 프론트 도메인을
# 추가한다. 로컬 개발 기본값은 localhost:3000.
_default_origins = "http://localhost:3000"
_cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", _default_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(auth.router)
app.include_router(members.router)
app.include_router(sessions.router)
app.include_router(assignments.router)
app.include_router(posture.router)
app.include_router(feedbacks.router)
app.include_router(reports.router)
app.include_router(me.router)
app.include_router(tasks.router)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_ROOT)), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok"}
