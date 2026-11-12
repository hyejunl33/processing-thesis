"""LLM adapters.

Default is `mock` so the whole web service runs without a model. Set
`LLM_MODE=ollama` to use a local Ollama server, or `LLM_MODE=api` later.
The important boundary: the LLM only produces ProblemSpec (relationships),
never BarModelSpec coordinates and never the final answer.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx

from .models import (
    HintRequest,
    HintResponse,
    ProblemSpec,
    Quantity,
    Relationship,
)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "90"))
LLM_MODE = os.getenv("LLM_MODE", "mock").lower()
LLM_FALLBACK = os.getenv("LLM_FALLBACK", "mock").lower()


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _extract_json(text: str) -> dict[str, Any]:
    text = _strip_fences(text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model output")
    return json.loads(text[start : end + 1])


def mock_parse(text: str) -> ProblemSpec:
    """A small heuristic parser for offline demos and tests.

    It intentionally handles only a couple of Korean comparison patterns.
    Real parsing is delegated to the local LLM.
    """

    # "사과가 3개 더 많습니다. 귤은 5개입니다."
    more = re.search(r"([가-힣]+)(?:이|가).{0,16}?(\d+(?:\.\d+)?)\s*[개명권마리]\s*더\s*많", text)
    known = re.findall(r"([가-힣]+)(?:은|는|이|가)\s*(\d+(?:\.\d+)?)\s*([개명권마리])", text)

    if more and known:
        more_label, diff = more.group(1), float(more.group(2))
        candidates = [k for k in known if k[0] != more_label]
        if candidates:
            known_label, known_value, unit = candidates[0][0], float(candidates[0][1]), candidates[0][2]
            return ProblemSpec(
                id="prob_mock_comp",
                original_text=text,
                problem_type="comparison",
                quantities=[
                    Quantity(id="q_known", label=known_label, value=known_value, unit=unit, role="known"),
                    Quantity(id="q_unknown", label=more_label, value=None, unit=unit, role="unknown"),
                ],
                relationships=[
                    Relationship(
                        type="difference",
                        left="q_unknown",
                        right="q_known",
                        difference=diff,
                        description=f"{more_label}가 {known_label}보다 {int(diff)}개 더 많음",
                    )
                ],
                unknown="q_unknown",
                confidence=0.55,
                warnings=["mock parser: heuristic pattern match"],
            )

    # Fallback: a stable demo problem so the UI is always usable offline.
    return ProblemSpec(
        id="prob_demo",
        original_text=text or "사과가 귤보다 3개 더 많습니다. 귤은 5개입니다. 사과는 몇 개일까요?",
        problem_type="comparison",
        quantities=[
            Quantity(id="q_orange", label="귤", value=5, unit="개", role="known"),
            Quantity(id="q_apple", label="사과", value=None, unit="개", role="unknown"),
        ],
        relationships=[
            Relationship(
                type="difference",
                left="q_apple",
                right="q_orange",
                difference=3,
                description="사과가 귤보다 3개 더 많음",
            )
        ],
        unknown="q_apple",
        confidence=0.3,
        warnings=["mock parser: fallback demo problem"],
    )


PARSE_PROMPT = """\
너는 초등 수학 문장제를 분석하는 도구다. 정답을 계산하지 마라.
문장제에 드러난 수량과 관계만 구조화해서 JSON으로만 답하라.

규칙:
- 모든 수량에 안정적인 id를 붙인다. (예: q_apple)
- role은 known, unknown, total 중 하나다.
- 관계는 difference(차이), part_whole(전체-부분), multiplicative(곱셈 비교) 중 하나다.
- difference 관계에는 difference 값을, part_whole에는 total 값을 가능한 범위에서 채운다.
- unknown은 반드시 quantities 안의 id 하나다.
- 확실하지 않은 값은 null로 두고 warnings에 적는다.
- JSON 외의 설명, 마크다운, 코드펜스를 출력하지 마라.

스키마:
{
  "id": "prob_001",
  "original_text": "...",
  "problem_type": "comparison | part_whole | multiplicative",
  "quantities": [{"id": "q_x", "label": "사과", "value": 5, "unit": "개", "role": "known"}],
  "relationships": [{"type": "difference", "left": "q_apple", "right": "q_orange", "difference": 3, "total": null, "description": "..."}],
  "unknown": "q_apple",
  "confidence": 0.0,
  "warnings": []
}

문장제:
{text}
"""


async def _ollama_chat(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "format": "json",
        "messages": [{"role": "user", "content": prompt}],
        "options": {"temperature": 0.1},
    }
    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        res = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
        res.raise_for_status()
        data = res.json()
        return data["message"]["content"]


async def parse_problem(text: str) -> ProblemSpec:
    if LLM_MODE != "ollama":
        return mock_parse(text)

    prompt = PARSE_PROMPT.format(text=text)
    try:
        raw = await _ollama_chat(prompt)
        try:
            return ProblemSpec.model_validate(_extract_json(raw))
        except Exception as first_error:  # noqa: BLE001 - repair loop
            repair_prompt = (
                f"{prompt}\n\n"
                "이전 출력이 스키마 검증을 통과하지 못했다. 오류를 고쳐 JSON만 다시 출력하라.\n"
                f"오류: {first_error}\n"
                f"이전 출력: {raw[:1200]}"
            )
            repaired = await _ollama_chat(repair_prompt)
            return ProblemSpec.model_validate(_extract_json(repaired))
    except Exception as exc:  # noqa: BLE001 - fallback is intentional
        if LLM_FALLBACK == "mock":
            spec = mock_parse(text)
            spec.warnings.append(f"ollama failed: {type(exc).__name__}: {exc}")
            return spec
        raise


HINT_PROMPT = """\
너는 초등 수학 학습을 돕는 발문 코치다.
절대 정답 숫자를 말하지 마라. 학생이 스스로 관계를 보도록 한 문장 질문만 하라.
한국어로 40자 이내. JSON으로만 답하라.

스키마: {{"text": "...", "focus": "bar_id 또는 null", "level": 1}}

문제 구조:
{problem}

막대 모델:
{model}

학생 상태:
{student_state}
"""


async def generate_hint(req: HintRequest) -> HintResponse:
    if LLM_MODE == "ollama":
        prompt = HINT_PROMPT.format(
            problem=req.problem.model_dump_json(),
            model=req.model.model_dump_json(),
            student_state=json.dumps(req.student_state, ensure_ascii=False),
        )
        try:
            raw = await _ollama_chat(prompt)
            data = _extract_json(raw)
            return HintResponse(
                text=str(data.get("text", "두 막대의 길이 차이를 먼저 살펴볼까?")),
                focus=data.get("focus"),
                level=int(data.get("level", 1)),
                source="ollama",
            )
        except Exception:  # noqa: BLE001
            if LLM_FALLBACK != "mock":
                raise

    unknown = req.model.unknown_bar
    return HintResponse(
        text="두 막대를 나란히 놓고, 길이 차이가 어디서 생기는지 먼저 찾아볼까?",
        focus=unknown,
        level=1,
        source="mock",
    )


async def llm_status() -> dict:
    if LLM_MODE != "ollama":
        return {"mode": LLM_MODE, "ok": True, "detail": "mock mode"}
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            res = await client.get(f"{OLLAMA_URL}/api/tags")
            res.raise_for_status()
            return {"mode": "ollama", "ok": True, "model": OLLAMA_MODEL}
    except Exception as exc:  # noqa: BLE001
        return {"mode": "ollama", "ok": False, "detail": str(exc)}
