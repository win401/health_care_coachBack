from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routers import assignments, auth, feedbacks, me, members, posture, reports, sessions, tasks

BACKEND_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BACKEND_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="FitNote Trainer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok"}
