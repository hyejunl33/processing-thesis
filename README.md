# Processing Graduation Thesis

광주교육대학교 컴퓨터교육과 졸업논문 프로젝트입니다.

## Status

- 2026-11-12: 주제 선정 및 졸업논문 작성계획서 작성 중
- 제약: **Processing 4 (Java mode)** 를 사용해 구현하고 배포한다.
- 목표: "Processing으로 만든 예쁜 데모"가 아니라, **측정 가능한 교육적 효과**와 **재현 가능한 엔지니어링 아티팩트**를 함께 남기는 것.

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

## Planned layout

```
.
├── docs/                 # 논문 계획, 설계 문서, 실험 프로토콜
├── sketch/               # Processing 4 Java mode 스케치
├── evaluation/           # 평가 도구, 로그 분석, 결과
├── scripts/              # 빌드·릴리스·데이터 파이프라인
└── submission/           # 학교 제출용 문서 (gitignore)
```

## Non-goals

- Processing을 단순 렌더링 도구로만 쓰고, 핵심 로직을 다른 스택에 숨기지 않는다.
- LLM/API가 없으면 데모가 아예 돌아가지 않는 구조를 만들지 않는다. 오프라인 폴백을 둔다.
- 교육적 효과를 측정하지 않은 채 "재미있었다"로 끝내지 않는다.
