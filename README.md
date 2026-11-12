# Processing Graduation Thesis

광주교육대학교 컴퓨터교육과 졸업논문 프로젝트입니다.

## Status

- 2026-11-12: 주제 선정 및 졸업논문 작성계획서 작성 중
- 제약: **Processing 4 (Java mode)** 를 사용해 구현하고 배포한다.
- 목표: "Processing으로 만든 예쁜 데모"가 아니라, **측정 가능한 교육적 효과**와 **재현 가능한 엔지니어링 아티팩트**를 함께 남기는 것.

## Candidate directions

| # | 가칭 | 한 줄 정의 | Processing의 역할 | 난이도 |
|---|---|---|---|---|
| 1 | **TraceCraft** | LLM이 만든 코드의 '결과'가 아니라 '실행 과정'을 보여주는 초등 코딩 학습 환경 | 실행 엔진 + 추적 시각화 + 로컬 서버 | 높음 |
| 2 | **Classroom Canvas** | 교실 안에서 도는 오프라인 실시간 과정중심 형성평가 서버 | HTTP/WebSocket 서버 + 대시보드 | 중간 |
| 3 | **Tangible Processing** | 인쇄한 카드와 웹캠으로 만드는 탠저블 프로그래밍 환경 | 비전 파이프라인 + 인터프리터 + 렌더러 | 중간~높음 |
| 4 | **SafeCanvas** | AI 생성 이미지를 '검수하는 눈'을 기르는 시각 QA 콘솔 | 이미지 분석 + 검수 UI + 감사 로그 | 중간 |

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
