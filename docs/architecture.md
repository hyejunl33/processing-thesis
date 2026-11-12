# Architecture — Python core + Processing visualization

> 결정일: 2026-11-12
> 현재 작업 가정: **MathLens** (초등 문장제 → 조작형 막대 모델)
> 핵심 결정: **하나의 웹서비스 안에서 핵심 로직은 Python, 시각화는 Processing 계열로 구현한다.**

## 0. 먼저 짚어야 할 제약

브라우저에서 도는 "Processing"은 사실상 **p5.js**다. Processing 4의 `.pde`(Java mode)는 JVM 앱이라 브라우저에서 직접 실행되지 않는다.

따라서 "하나의 웹서비스 + Processing 시각화"는 세 가지 구현 경로가 있다.

| 경로 | 실제 구현 | 장점 | 단점 |
|---|---|---|---|
| A. p5.js (권장) | 브라우저에서 p5.js 캔버스 | 진짜 웹서비스, 인터랙션 자연스러움, 배포 쉬움 | `.pde`가 아니라 JS라는 지적 가능 |
| B. Processing Java 렌더 워커 | 서버에서 headless Processing이 PNG/SVG/프레임 생성, 브라우저가 표시 | `.pde`를 실제로 사용 | 인터랙션마다 렌더 요청 → 지연, 배포 복잡 |
| C. Processing Java 데스크톱 클라이언트 | `.pde` 앱이 Python 웹 API를 호출 | `.pde` + 풍부한 인터랙션 | "하나의 웹서비스"는 아니고 클라이언트-서버 |

**이 문서의 기본안은 A(p5.js) + B를 언제든 끼울 수 있는 계약 구조다.**  
즉, 시각화 입력을 `BarModelSpec` JSON으로 고정하고, p5.js 렌더러와 Processing Java 렌더러가 **같은 스펙을 소비**하게 만든다. 학과에서 `.pde`를 요구하면 B/C로 갈아끼운다.

> 학과에 확인할 질문: "Processing을 사용하라"는 것이 ① `.pde`(Java mode)만 인정인지, ② p5.js를 포함한 Processing 계열을 인정하는지. 이 답에 따라 A/B/C를 확정한다.

## 1. 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│                        One Web Service                       │
│                                                             │
│  ┌──────────────────────┐        ┌───────────────────────┐  │
│  │  Frontend (p5.js)    │  HTTP  │  Backend (FastAPI)    │  │
│  │  - Bar model canvas  │ ─────▶ │  - LLM orchestration  │  │
│  │  - Drag / drop       │ ◀───── │  - Schema validation  │  │
│  │  - Hint panel        │  JSON  │  - Repair loop        │  │
│  │  - Event logging     │        │  - Session / SQLite   │  │
│  └──────────────────────┘        │  - Evaluation logs    │  │
│                                  └───────────┬───────────┘  │
│                                              │ HTTP          │
│                                  ┌───────────▼───────────┐  │
│                                  │  Model Runtime        │  │
│                                  │  - Ollama (local)     │  │
│                                  │  - OpenAI/Gemini API  │  │
│                                  │  - Python sidecar     │  │
│                                  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

- **FastAPI**가 정적 프론트엔드(p5.js)와 API를 함께 서빙한다. → 하나의 웹서비스.
- 모델은 **Ollama(로컬)** 기본, **API** 폴백/비교군.
- OCR/VLM이 필요하면 Python sidecar를 추가하되, 핵심 앱은 모델이 없어도 mock/캐시로 동작하게 한다.
- `ProcessingRenderer`는 교체 가능한 어댑터다. p5.js가 기본, `.pde` 렌더러가 대안.

## 2. 계약(Contract)이 중심이다

시각화가 p5.js든 Processing Java든, **입력 스펙은 하나**여야 한다. 이게 이 아키텍처의 핵심 이음새(seam)다.

### 2.1 ProblemSpec — Python이 만드는 문제 구조

```json
{
  "id": "prob_001",
  "original_text": "사과가 3개 더 많습니다. 귤은 5개입니다. 사과는 몇 개일까요?",
  "problem_type": "comparison",
  "quantities": [
    {"id": "q_orange", "label": "귤", "value": 5, "unit": "개", "role": "known"},
    {"id": "q_apple", "label": "사과", "value": null, "unit": "개", "role": "unknown"}
  ],
  "relationships": [
    {"type": "difference", "left": "q_apple", "right": "q_orange", "difference": 3,
     "description": "사과가 귤보다 3개 더 많다"}
  ],
  "unknown": "q_apple",
  "confidence": 0.93
}
```

### 2.2 BarModelSpec — Processing이 그리는 시각화 스펙

```json
{
  "problem_id": "prob_001",
  "type": "comparison",
  "bars": [
    {"id": "bar_orange", "label": "귤", "value": 5, "segments": [{"value": 5, "color": "#F2B84B"}]},
    {"id": "bar_apple", "label": "사과", "value": null, "segments": [
      {"value": 5, "color": "#7FB3D5"},
      {"value": 3, "color": "#E59866", "label": "+3"}
    ]}
  ],
  "annotations": [
    {"type": "difference", "from": "bar_orange", "to": "bar_apple", "label": "3개 더"}
  ],
  "unknown_bar": "bar_apple",
  "scale": {"unit_px": 42, "max_value": 10},
  "interaction": {"draggable": ["bar_apple"], "editable_values": true}
}
```

> 중요한 원칙: **LLM은 `BarModelSpec`을 직접 그리지 않는다.** LLM은 `ProblemSpec`(관계 구조)만 만들고, `BarModelSpec`은 Python의 결정적 레이아웃 알고리즘이 만든다. 이래야 좌표가 흔들리지 않고, 재현·평가가 가능하다.

### 2.3 Event — 학생 조작 로그

```json
{
  "session_id": "s_001",
  "problem_id": "prob_001",
  "ts": 1763000000,
  "type": "drag_value",
  "target": "bar_apple",
  "payload": {"from": null, "to": 8},
  "hint_level": 1
}
```

이 로그가 논문의 분석 데이터다. p5.js든 Processing이든 **같은 이벤트 스키마**를 보낸다.

## 3. API 초안

| Method | Path | 역할 |
|---|---|---|
| `POST` | `/api/problems/parse` | 문장제 텍스트 → `ProblemSpec` (LLM + 검증/repair) |
| `POST` | `/api/models/build` | `ProblemSpec` → `BarModelSpec` (결정적 레이아웃) |
| `POST` | `/api/hints` | 학생 상태 → 발문/힌트 (LLM, 정답 비노출) |
| `POST` | `/api/events` | 조작 이벤트 로그 저장 |
| `GET` | `/api/sessions/{id}/report` | 세션 요약/교사용 리포트 |
| `GET` | `/api/health` | 헬스체크 + 모델 상태 |

## 4. Python 쪽 책임

- LLM 호출/프롬프트/JSON 스키마 검증/repair loop/캐시.
- `ProblemSpec` 검증(수량, 관계, 미지수 일관성).
- `BarModelSpec` 레이아웃 알고리즘(단위, 최대값, 막대 길이, 주석 위치).
- 힌트 정책: 정답 숫자를 직접 말하지 않기, 단계별 발문, 학생 상태 기반.
- 세션/이벤트 저장(SQLite로 시작, 필요 시 Postgres).
- 평가용 로그 내보내기(CSV/JSON), 재현 가능한 시드.

## 5. Processing/p5.js 쪽 책임

- `BarModelSpec`을 받아 캔버스에 렌더링.
- 막대 드래그, 값 입력, 주석/하이라이트, 힌트 패널.
- `Event`를 API로 전송.
- **로컬 렌더링만** 담당하고, 문제 해석/정답 계산은 하지 않는다. (경계 유지)

### p5.js 기본안

- `frontend/sketch.js`에서 `setup()`/`draw()` 사용.
- `BarModelSpec`을 `fetch`로 받아 그림.
- 드래그/클릭 이벤트를 `/api/events`로 전송.
- FastAPI가 `frontend/`를 정적 서빙.

### Processing Java 대안

- `processing/BarModelRenderer/BarModelRenderer.pde`가 같은 `BarModelSpec` JSON을 읽어 렌더링.
- 서버 렌더링이 필요하면 `processing-java --run`을 headless(Xvfb)로 실행하고 PNG를 반환.
- 데스크톱 클라이언트가 필요하면 Processing 앱이 FastAPI를 호출.

## 6. 배포

- **단일 컨테이너:** FastAPI + 정적 p5.js. `uvicorn app.main:app`.
- **모델:** Ollama는 호스트 또는 별도 컨테이너. API 모드면 외부 API.
- **개발:** `docker compose up` 또는 `uvicorn --reload`.
- **데모:** 로컬 Ollama가 없으면 mock/캐시 모드로 전체 흐름이 돌아가게 한다. (심사/발표 환경 대비)
- **관측성:** `/api/health`에 모델 연결 상태, 평균 지연, 마지막 오류를 노출.

## 7. 논문에서의 정당화

- "Processing은 시각화와 상호작용을 담당하고, Python은 AI/검증/로그를 담당한다"는 **역할 분리**를 설계 결정으로 서술.
- 시각화 스펙(`BarModelSpec`)을 고정해 **p5.js와 Processing Java 렌더러를 교체 가능**하게 만든 것이 엔지니어링 기여.
- 로컬 LLM vs API의 **정확도/지연/비용** 비교를 부수적 RQ로 넣을 수 있다.
- 평가는 이벤트 로그 기반으로 재현 가능.

## 8. 리스크와 대응

| 리스크 | 대응 |
|---|---|
| 학과가 p5.js를 Processing으로 인정하지 않음 | `BarModelSpec` 렌더러를 Processing Java로 구현, B/C 경로로 전환 |
| LLM이 관계 구조를 잘못 뽑음 | JSON 스키마 검증 + repair + 교사/학생 수정 UI |
| 로컬 모델이 느림 | 3B/4B 양자화, 캐시, 스트리밍, API 폴백 |
| 웹서비스 배포가 무거움 | 단일 FastAPI 컨테이너 + 정적 파일, Ollama는 선택 |
| 학생 조작 로그가 개인정보를 포함 | 익명 세션 ID, 텍스트 최소화, 보관 기간 정책 |
