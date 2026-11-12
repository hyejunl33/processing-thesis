# Processing Graduation Thesis

광주교육대학교 컴퓨터교육과 졸업논문 프로젝트입니다.

## Status

- 2026-11-12: 주제 선정 및 졸업논문 작성계획서 작성 중
- 제약: **Processing**을 사용해 시각화를 구현하고 배포한다.
- 아키텍처 결정: **하나의 웹서비스 안에서 핵심 로직은 Python, 시각화는 Processing 계열.**
- 목표: "Processing으로 만든 예쁜 데모"가 아니라, **측정 가능한 교육적 효과**와 **재현 가능한 엔지니어링 아티팩트**를 함께 남기는 것.

## Current architecture (MathLens)

```
[Processing/p5.js canvas]  <--HTTP/JSON-->  [FastAPI Python core]  <--HTTP-->  [Ollama / API]
   막대 모델 렌더링                              문제 구조화/검증/힌트/로그
   드래그/슬라이더                                BarModelSpec 레이아웃
```

- 계약: `ProblemSpec` → `BarModelSpec` → `Event`. LLM은 좌표를 만들지 않고, 정답도 말하지 않는다.
- `BarModelSpec`은 p5.js와 Processing Java 렌더러가 **공유**한다. 학과에서 `.pde`를 요구하면 렌더러만 교체한다.
- 자세한 내용: [`docs/architecture.md`](docs/architecture.md)

### Quick start

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
# http://localhost:8000
```

기본은 `LLM_MODE=mock`이라 모델 없이 전체 흐름이 돈다. 로컬 LLM을 쓰려면:

```bash
ollama pull qwen2.5:7b
LLM_MODE=ollama OLLAMA_MODEL=qwen2.5:7b PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

Docker:

```bash
docker compose up --build
```

테스트:

```bash
PYTHONPATH=backend pytest backend/tests -q
```

## Candidate directions (v2)

> v1은 `docs/archive/ideas-v1.md`에 보관. v2의 기준: **교육현장의 실제 문제 + AI가 코어(로컬/API) + Processing이 구현체**.

| # | 가칭 | 한 줄 정의 | AI | Processing의 역할 | 난이도 |
|---|---|---|---|---|---|
| 1 | **MathLens** | 문장제를 조작 가능한 막대 모델로 번역하는 AI | 로컬 LLM/API (스키마 추출) | 조작형 시각화 + 로그 + 로컬 서버 | 중간 |
| 2 | **ReadEcho** | 로컬 음성인식으로 읽기 유창성을 코칭 | whisper.cpp + LLM | 오디오 시각화 + 정렬 + 대시보드 | 높음 |
| 3 | **EvidenceLens** | 학생 작품의 근거를 비추는 AI 피드백 콘솔 | 로컬/API VLM | 이미지 주석 + 루브릭 + 감사 로그 | 중간 |
| 4 | **LessonLens** | 교육과정 근거 기반 수업 설계 RAG | 로컬 임베딩 + LLM | 교육과정 그래프 + 출처 뷰어 | 낮음~중간 |
| + | **FracLens** | 분수 조작교구 위의 AI (와일드카드) | 비전 + LLM | 카메라 + AR 오버레이 + 발문 | 높음 |

자세한 비교와 설계 초안은 [`docs/ideas.md`](docs/ideas.md)를 참고하세요.

## Current layout

```
.
├── backend/              # FastAPI: LLM, 스키마 검증, 레이아웃, 로그
│   ├── app/
│   └── tests/
├── frontend/             # Processing(p5.js): 막대 모델, 드래그, 이벤트
├── docs/                 # 논문 계획, 아키텍처, 실험 프로토콜
├── data/                 # SQLite 이벤트 로그 (gitignore)
├── Dockerfile
└── docker-compose.yml
```

## Non-goals

- LLM이 정답을 대신 말하거나, 좌표까지 생성하게 하지 않는다.
- LLM/API가 없으면 데모가 아예 돌아가지 않는 구조를 만들지 않는다. mock/캐시 폴백을 둔다.
- 교육적 효과를 측정하지 않은 채 "재미있었다"로 끝내지 않는다.
- Python과 Processing 사이의 경계를 숨기지 않는다. 논문에 역할 분리를 명시한다.
