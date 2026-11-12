"""FastAPI entrypoint: Python core + Processing/p5.js visualization."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import llm, store
from .layout import build_bar_model, resolve_unknown_value
from .models import BarModelSpec, Event, HintRequest, HintResponse, ProblemSpec

ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = Path(os.getenv("FRONTEND_DIR", str(ROOT / "frontend")))


@asynccontextmanager
async def lifespan(app: FastAPI):
    store.init_db()
    yield


app = FastAPI(
    title="MathLens API",
    description="Python core for parsing, layout, hints, and logs; Processing/p5.js for visualization.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only; tighten for deployment
    allow_methods=["*"],
    allow_headers=["*"],
)


class ParseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class CheckRequest(BaseModel):
    problem: ProblemSpec
    answer: float


class CheckResponse(BaseModel):
    correct: bool
    expected: float | None = None
    message: str


@app.get("/api/health")
async def health() -> dict:
    return {"ok": True, "llm": await llm.llm_status()}


@app.post("/api/problems/parse", response_model=ProblemSpec)
async def parse_problem(req: ParseRequest) -> ProblemSpec:
    return await llm.parse_problem(req.text)


@app.post("/api/models/build", response_model=BarModelSpec)
def build_model(problem: ProblemSpec) -> BarModelSpec:
    return build_bar_model(problem)


@app.post("/api/hints", response_model=HintResponse)
async def hints(req: HintRequest) -> HintResponse:
    return await llm.generate_hint(req)


@app.post("/api/check", response_model=CheckResponse)
def check_answer(req: CheckRequest) -> CheckResponse:
    expected = resolve_unknown_value(req.problem)
    if expected is None:
        return CheckResponse(correct=False, message="아직 답을 계산할 수 없어요. 관계를 먼저 확인해보자.")
    correct = abs(expected - req.answer) < 1e-6
    return CheckResponse(
        correct=correct,
        expected=expected,
        message="맞았어요!" if correct else "막대의 길이 차이를 다시 확인해볼까?",
    )


@app.post("/api/events")
def save_event(event: Event) -> dict:
    return {"id": store.save_event(event)}


@app.get("/api/sessions/{session_id}/report")
def get_report(session_id: str) -> dict:
    return store.session_report(session_id)


# Static frontend must be mounted last so /api/* and /docs keep working.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
