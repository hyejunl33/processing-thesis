"""Deterministic layout: ProblemSpec -> BarModelSpec.

The LLM must never produce coordinates. It only produces the problem structure;
this module turns that structure into a stable, reproducible visual spec.
"""

from __future__ import annotations

from .models import (
    Annotation,
    Bar,
    BarModelSpec,
    BarSegment,
    Interaction,
    ProblemSpec,
    Quantity,
    Scale,
)

KNOWN_COLOR = "#7FB3D5"
UNKNOWN_COLOR = "#AED6F1"
DIFFERENCE_COLOR = "#E59866"
TOTAL_COLOR = "#A9DFBF"
PART_COLORS = ["#7FB3D5", "#F5B041", "#A9DFBF", "#C39BD3", "#F1948A"]


def _resolve_values(problem: ProblemSpec) -> dict[str, float | None]:
    values: dict[str, float | None] = {q.id: q.value for q in problem.quantities}

    # A few passes handle simple chains (known -> unknown -> other unknown).
    for _ in range(len(problem.relationships) + 1):
        changed = False
        for rel in problem.relationships:
            if rel.type == "difference" and rel.difference is not None:
                left, right = values.get(rel.left), values.get(rel.right)
                if left is None and right is not None:
                    values[rel.left] = right + rel.difference
                    changed = True
                elif right is None and left is not None:
                    values[rel.right] = left - rel.difference
                    changed = True
            elif rel.type == "part_whole":
                total_ids = [q.id for q in problem.quantities if q.role == "total"]
                total_id = total_ids[0] if total_ids else None
                if total_id and values.get(total_id) is not None:
                    parts = [q.id for q in problem.quantities if q.role == "known" and q.id != total_id]
                    unknown_parts = [q.id for q in problem.quantities if q.role == "unknown" and q.id != total_id]
                    if len(unknown_parts) == 1:
                        known_sum = sum(v for i in parts if (v := values.get(i)) is not None)
                        values[unknown_parts[0]] = values[total_id] - known_sum
                        changed = True
                elif total_id and values.get(total_id) is None:
                    known = [values.get(q.id) for q in problem.quantities if q.role == "known"]
                    if all(v is not None for v in known):
                        values[total_id] = sum(known)  # type: ignore[arg-type]
                        changed = True
        if not changed:
            break
    return values


def _segments_for(
    q: Quantity,
    values: dict[str, float | None],
    problem: ProblemSpec,
) -> list[BarSegment]:
    value = values.get(q.id)
    if value is None:
        return [BarSegment(value=0, color=UNKNOWN_COLOR, label="?")]

    if q.role == "total":
        parts = [x for x in problem.quantities if x.role == "known" and x.id != q.id]
        segments = []
        for i, part in enumerate(parts):
            part_value = values.get(part.id)
            if part_value is None:
                continue
            segments.append(
                BarSegment(
                    value=part_value,
                    color=PART_COLORS[i % len(PART_COLORS)],
                    label=part.label,
                )
            )
        return segments or [BarSegment(value=value, color=TOTAL_COLOR)]

    # Show "known part + difference" when the unknown is the larger comparison bar.
    for rel in problem.relationships:
        if rel.type == "difference" and rel.left == q.id and rel.difference is not None:
            base = values.get(rel.right)
            if base is not None and base >= 0:
                return [
                    BarSegment(value=base, color=KNOWN_COLOR, label=None),
                    BarSegment(value=rel.difference, color=DIFFERENCE_COLOR, label=f"+{_fmt(rel.difference)}"),
                ]

    return [BarSegment(value=value, color=UNKNOWN_COLOR if q.role == "unknown" else KNOWN_COLOR)]


def resolve_unknown_value(problem: ProblemSpec) -> float | None:
    return _resolve_values(problem).get(problem.unknown)


def _fmt(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:g}"


def build_bar_model(problem: ProblemSpec) -> BarModelSpec:
    values = _resolve_values(problem)
    quantities = problem.quantities

    numeric_values = [v for v in values.values() if v is not None and v > 0]
    max_value = max(numeric_values, default=1.0)
    max_value = max(max_value, 1.0)
    unit_px = min(52.0, 560.0 / max_value)

    bars: list[Bar] = []
    for q in quantities:
        # Never send the unknown's numeric answer to the renderer: the bar length
        # is the visual representation, but the label stays "?".
        display_value = None if q.role == "unknown" else values.get(q.id)
        bars.append(
            Bar(
                id=q.id,
                label=q.label,
                value=display_value,
                segments=_segments_for(q, values, problem),
            )
        )

    annotations: list[Annotation] = []
    for rel in problem.relationships:
        if rel.type == "difference":
            annotations.append(
                Annotation(
                    type="difference",
                    from_bar=rel.right,
                    to_bar=rel.left,
                    label=rel.description or f"{_fmt(rel.difference or 0)}개 차이",
                )
            )
        elif rel.type == "part_whole":
            annotations.append(
                Annotation(type="total", from_bar=None, to_bar=None, label=rel.description or "전체와 부분")
            )

    return BarModelSpec(
        problem_id=problem.id,
        type=problem.problem_type,
        bars=bars,
        annotations=annotations,
        unknown_bar=problem.unknown,
        scale=Scale(unit_px=unit_px, max_value=max_value),
        interaction=Interaction(draggable=[problem.unknown], editable_values=True),
    )
