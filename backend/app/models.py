"""Pydantic contracts shared by the Python core and the Processing/p5.js renderer."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Quantity(BaseModel):
    id: str
    label: str
    value: float | None = None
    unit: str = "개"
    role: Literal["known", "unknown", "total"] = "known"


class Relationship(BaseModel):
    type: Literal["difference", "part_whole", "multiplicative"]
    left: str
    right: str
    difference: float | None = None
    total: float | None = None
    description: str = ""


class ProblemSpec(BaseModel):
    id: str
    original_text: str
    problem_type: str = "comparison"
    quantities: list[Quantity]
    relationships: list[Relationship]
    unknown: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_ids(self) -> "ProblemSpec":
        ids = {q.id for q in self.quantities}
        if self.unknown not in ids:
            raise ValueError(f"unknown quantity {self.unknown!r} not found")
        for rel in self.relationships:
            if rel.left not in ids or rel.right not in ids:
                raise ValueError(f"relationship references missing quantity: {rel}")
        return self


class BarSegment(BaseModel):
    value: float
    color: str
    label: str | None = None


class Bar(BaseModel):
    id: str
    label: str
    value: float | None
    segments: list[BarSegment]


class Annotation(BaseModel):
    type: Literal["difference", "total", "unknown"]
    from_bar: str | None = None
    to_bar: str | None = None
    label: str = ""


class Scale(BaseModel):
    unit_px: float
    max_value: float


class Interaction(BaseModel):
    draggable: list[str] = Field(default_factory=list)
    editable_values: bool = True


class BarModelSpec(BaseModel):
    problem_id: str
    type: str
    bars: list[Bar]
    annotations: list[Annotation] = Field(default_factory=list)
    unknown_bar: str
    scale: Scale
    interaction: Interaction = Field(default_factory=Interaction)


class HintRequest(BaseModel):
    problem: ProblemSpec
    model: BarModelSpec
    student_state: dict = Field(default_factory=dict)
    history: list[dict] = Field(default_factory=list)


class HintResponse(BaseModel):
    text: str
    focus: str | None = None
    level: int = 1
    source: str = "mock"


class Event(BaseModel):
    session_id: str
    problem_id: str | None = None
    ts: float
    type: str
    target: str | None = None
    payload: dict = Field(default_factory=dict)
