# Persona 기반 신뢰성 있는 답변 — 2026 프로젝트 지형

> 작성일: 2026-11-12
> 질문: "persona 기반으로 신뢰할 수 있는 답변"을 만들 때, 현존하는 가장 신뢰도 높은 persona 프로젝트/데이터셋/벤치마크는 무엇인가?
> 결론 요약: **단일 최강 프로젝트는 없다.** persona의 종류(사용자/캐릭터/전문가/합성 시뮬레이션)에 따라 최적해가 다르고, 신뢰성은 persona 데이터가 아니라 **검색·근거·검증·거절·메모리** 아키텍처에서 나온다.

## 0. 먼저 바로잡을 전제

- **Nemotron-Personas는 "오래된" 데이터가 아니다.** NVIDIA의 Nemotron-Personas는 다국어·지역별 synthetic persona 데이터 컬렉션이고, 한국어 버전 `Nemotron-Personas-Korea`는 2026년에도 업데이트되고 있다. 컬렉션 기준 약 700만 규모의 한국어 synthetic personas를 표방한다.
- 다만 **synthetic persona dataset은 "신뢰할 수 있는 답변"의 사실 근거가 아니다.** 이는 사용자/평가 대상의 분포를 넓히는 데이터이지, 지식의 ground truth가 아니다.
- 사용자가 말한 "Nemotron Persona"가 `Nemotron-Personas-Korea`인지, 2024년 Nemotron-4 계열의 persona prompting/데이터인지에 따라 의미가 다르다. 전자면 최신 데이터이고, 후자면 모델/레시피에 가깝다.

## 1. Persona를 네 가지로 나눠야 한다

| 유형 | persona가 하는 일 | 신뢰성의 원천 | 대표 프로젝트 |
|---|---|---|---|
| **사용자 개인화** | 사용자의 선호·제약·이력을 반영 | 사용자 데이터 + 검색 + 메모리 | PersonaMem-v2, PersonaFeedback, LaMP-QA, PersonaLens |
| **역할/캐릭터** | 말투·가치관·지식 경계를 유지 | 일관성 평가 + 지식 경계 + 안전 | PersonaGym, CHARM, CharacterEval, RoleBench |
| **전문가 페르소나** | 특정 전문가처럼 설명·판단 | 권위 있는 RAG + 인용 + 거절 | SCOPE(구성) + RAG + CHARM + PersonaGym |
| **합성 사용자 시뮬레이션** | 실제 사용자 대신 반응 시뮬레이션 | 실제 인간 데이터와의 정합성 | SCOPE, Nemotron-Personas, PersonaHub, PERSONA |

"persona 기반 신뢰할 수 있는 답변"을 만들려면 먼저 **어느 유형인지** 정해야 한다. 유형을 섞으면 "그럴듯하지만 틀린" 답변이 나오기 쉽다.

## 2. 2025–2026 주요 프로젝트

### 2.1 사용자 개인화 / 개인화 QA

| 프로젝트 | 무엇인가 | 강점 | 한계 |
|---|---|---|---|
| **PersonaFeedback** (2025) | 명시적 persona가 주어졌을 때 개인화 응답 품질을 평가하는 인간 주석 벤치마크. 200 personas, 8,298 test cases | persona inference와 personalization을 분리해 평가. hard tier는 최신 LLM도 어려움 | explicit persona에 한정. 실제 서비스의 암묵적 선호 추론은 별개 |
| **LaMP-QA** (2025) | personalized long-form QA 벤치마크. Arts/Lifestyle/Society 45+ subcategories | 개인화 컨텍스트가 최대 39% 성능 향상. long-form 답변 평가에 적합 | 영어 중심. 한국어 도메인은 별도 구축 필요 |
| **PersonaMem-v2** (2025) | 1,000개의 현실적 user-chatbot interactions, 300+ scenarios, 20,000+ preferences, 128k context | implicit preference를 다룸. agentic memory로 55% 정확도, 16x 적은 토큰(2k memory) | frontier LLM도 37–48%에 그침. 개인화가 얼마나 어려운지 보여줌 |
| **PersonaLens** (2025) | personalization evaluation benchmark | assistant model 평가에 특화 | 태스크/도메인 범위 확인 필요 |
| **LaMP** (2023–) | personalized language modeling benchmark | 오래 검증된 baseline | 최신 long-form QA/agent memory는 별도 |

**핵심 인사이트:** PersonaFeedback은 "retrieval-augmented framework가 personalization의 de facto solution이 아니다"라고 명시한다. **RAG를 붙였다고 개인화가 해결되지 않는다.** persona를 어떻게 표현하고, 어떤 근거를 검색하고, 어떻게 검증하는지가 중요하다.

### 2.2 역할/캐릭터 일관성

| 프로젝트 | 무엇인가 | 강점 | 한계 |
|---|---|---|---|
| **PersonaGym** (2024, EMNLP Findings 2025) | 200 personas × 10,000 questions로 persona agent를 동적 평가. PersonaScore(decision theory 기반) | persona 충실도/일관성을 자동·대규모 평가. 모델 크기가 persona 능력을 보장하지 않음을 보여줌 | persona *일관성*이지 *사실성*은 아님 |
| **CHARM** (2026) | 40개 real/fictional characters, 5개 문화권. Temporal/Cross-Universe 지식 경계 평가 | hallucination을 ① 경계 인식 실패 ② 경계 준수 실패로 분리. 최신 모델도 "모르면서 답하는" compliance failure가 큼 | 캐릭터 role-play 특화. 일반 업무 persona와 다름 |
| **CharacterEval / RoleBench / InCharacter** | 중국어/영어 role-play 평가 | 캐릭터성·대화 품질 평가에 유용 | 최신 persona agent/지식 경계 평가와는 초점이 다름 |

**핵심 인사이트:** CHARM은 "지식 경계를 아는 것"과 "모른다고 말하는 것"이 다르다는 것을 보여준다. 신뢰할 수 있는 persona 답변에는 **knowledge boundary + abstention policy**가 필수다.

### 2.3 합성 persona / 사용자 시뮬레이션

| 프로젝트 | 무엇인가 | 강점 | 한계 |
|---|---|---|---|
| **SCOPE** (2026) | 141-item, 2-hour sociopsychological protocol 기반 persona 구성·평가 프레임워크. 124명 미국 참가자 | 인구통계만으로는 인간 응답 유사성 분산의 ~1.5%만 설명. 가치·정체성·사회심리 facets가 예측력↑. SimBench에서 Nemotron personas보다 우수 | 미국 참가자 기반. 한국어/한국 사회맥락은 별도 검증 필요 |
| **Nemotron-Personas-Korea** (2026) | 한국 인구·지리·사회 분포에 기반한 대규모 synthetic personas. 한국어 | 한국어 coverage, 상업적 사용 가능 라이선스(데이터셋 카드 확인) | synthetic. 실제 한국인을 대표한다고 가정하면 위험 |
| **PersonaHub** (2024) | 웹 데이터에서 큐레이션한 10억 personas | 스케일, 다양한 관점, synthetic data 생성 | synthetic/자동 큐레이션. 개별 persona의 현실성·일관성 보장 어려움 |
| **PERSONA** (2024, COLING 2025) | US census 기반 1,586 synthetic personas, 3,868 prompts, 317,200 feedback pairs | pluralistic alignment 평가 재현 가능 | synthetic persona 기반. 실제 사용자 대표성은 제한 |

**핵심 인사이트:** SCOPE의 결과는 "인구통계 템플릿 persona는 구조적 병목"이라는 강한 메시지다. **나이/성별/직업만 채운 persona는 신뢰성에 거의 기여하지 않는다.** 가치관, 정체성, 사회심리적 맥락, 행동 이력이 중요하다.

### 2.4 안전/제어

| 프로젝트 | 무엇인가 | 강점 | 한계 |
|---|---|---|---|
| **Persona Vectors** (2025) | 모델 activation space에서 evil/sycophancy/hallucination 등 trait 방향을 찾아 모니터링·steering | 배포 시 persona 변화 감지, fine-tuning 후 유해 trait 예측/완화 | 모델 내부 접근 필요. API 모델에는 적용 어려움 |
| **"LLM Generated Persona is a Promise with a Catch"** (NeurIPS 2025 position) | 합성 persona의 한계·과긍정 편향·타당성 문제 제기 | synthetic persona를 맹신하지 말라는 경고 | position paper. 대안 아키텍처는 별도 |

## 3. "가장 신뢰도 높은" 선택은 단일 프로젝트가 아니다

### 3.1 목적별 추천

| 목적 | 1순위 | 2순위 | 이유 |
|---|---|---|---|
| **한국어 synthetic persona coverage** | Nemotron-Personas-Korea | PERSONA / PersonaHub | 한국어·인구 분포 coverage. 단, synthetic 한계 명시 |
| **persona 구성의 현실성** | SCOPE | PERSONA | 사회심리적 facets가 인구통계보다 예측력 높음 |
| **개인화 응답 평가** | PersonaFeedback | LaMP-QA, PersonaLens | 인간 주석, explicit persona, long-form QA |
| **동적 사용자 메모리** | PersonaMem-v2 | LaMP | implicit preference, agentic memory |
| **persona 일관성** | PersonaGym | CharacterEval, RoleBench | 200 personas, 10k questions, PersonaScore |
| **지식 경계/할루시네이션** | CHARM | PersonaGym | boundary-awareness vs compliance 분리 |
| **안전/편향/아첨 제어** | Persona Vectors | — | sycophancy/hallucination trait 모니터링 |
| **pluralistic alignment** | PERSONA | — | 재현 가능한 testbed |

### 3.2 실무 스택 제안

```
[Persona schema]
  - 인구통계 + 가치/정체성 + 사회심리 facets + 행동 이력
  - 지식 경계(knowledge boundary) + 말투/금기 + 목표
        │
        ▼
[Retrieval]
  - 신뢰 코퍼스 + citation
  - persona-conditioned query expansion
        │
        ▼
[Generation]
  - persona prompt + evidence + uncertainty
  - "모르면 말하지 않는다" 정책
        │
        ▼
[Verification]
  - claim-evidence entailment
  - persona consistency (PersonaGym)
  - knowledge boundary (CHARM)
  - sycophancy/hallucination (Persona Vectors)
        │
        ▼
[Memory]
  - human-readable, editable, 2k-token memory (PersonaMem-v2 스타일)
        │
        ▼
[Evaluation]
  - personalization: PersonaFeedback / LaMP-QA
  - consistency: PersonaGym
  - faithfulness: RAG faithfulness (FaithJudge/RAGAS)
  - human audit
```

## 4. 신뢰성에 대한 냉정한 현실

1. **persona ≠ fact.** persona는 답변의 관련성·일관성·스타일을 높이지만, 사실성을 보장하지 않는다. 오히려 role-play는 hallucination을 늘릴 수 있다.
2. **synthetic persona ≠ real user.** Nemotron/PersonaHub/PERSONA는 coverage와 simulation에는 유용하지만, 실제 사용자 대표성이나 사실 근거로 쓰면 안 된다.
3. **인구통계 persona는 약하다.** SCOPE: 인구통계만으로 인간 응답 유사성 분산의 ~1.5%만 설명.
4. **RAG가 personalization을 자동 해결하지 않는다.** PersonaFeedback: retrieval-augmented framework가 de facto solution이 아님.
5. **일관성 ≠ 사실성.** PersonaGym 점수가 높아도 사실 오류가 있을 수 있다. 별도 faithfulness 평가가 필요.
6. **지식 경계를 아는 것과 지키는 것은 다르다.** CHARM: 최신 모델도 경계를 알면서도 out-of-character 사실을 답하는 compliance failure가 큼.
7. **행동 이력이 persona 설명보다 강할 수 있다.** "Behavioral History Outperforms Descriptions of the Person" (2026) — 실제 선택/행동 로그가 서술형 persona보다 예측력이 높다.
8. **persona는 상태(state)이지 속성(attribute)이 아니다.** "Personas Are Not People: Identity as State, Not Attribute" (2026) — 대화/맥락에 따라 업데이트되는 것으로 모델링해야 한다.

## 5. 다음 단계 제안

1. **persona 유형을 먼저 고정**: 사용자 개인화 / 전문가 역할 / 캐릭터 / 합성 시뮬레이션.
2. **100–300개 평가셋**을 직접 만든다: 질문, 정답/근거, persona 적합성, 지식 경계 케이스.
3. **baseline 비교**: ① persona 없음 ② persona prompt ③ persona + RAG ④ persona + RAG + verification.
4. **지표**: personalization (PersonaFeedback/LaMP-QA), consistency (PersonaGym), faithfulness (claim-evidence), abstention (CHARM), sycophancy (Persona Vectors).
5. **한국어 검증**: Nemotron-Personas-Korea는 coverage용, 실제 사용자 인터뷰/로그로 타당화.

## 6. 참고 링크

- Nemotron-Personas collection: https://huggingface.co/collections/nvidia/nemotron-personas
- SCOPE (2026): https://arxiv.org/abs/2601.07110
- PersonaFeedback (2025): https://arxiv.org/abs/2506.12915
- PersonaMem-v2 (2025): https://arxiv.org/abs/2512.06688
- PersonaGym (2024/2025): https://arxiv.org/abs/2407.18416
- CHARM (2026): https://arxiv.org/abs/2609.01352
- Persona Vectors (2025): https://arxiv.org/abs/2507.21509
- LaMP-QA (2025): https://arxiv.org/abs/2506.00137
- PERSONA (2024/2025): https://arxiv.org/abs/2407.17387
- PersonaHub (2024): https://arxiv.org/abs/2406.20094
- Behavioral History Outperforms Descriptions of the Person (2026): https://arxiv.org/html/2610.03998v1
- Personas Are Not People: Identity as State, Not Attribute (2026): https://arxiv.org/html/2611.05292v1

## 7. Nemotron-Personas 실사용 주의사항

### 7.1 Nemotron은 "설문 패널"이 아니다

NVIDIA 문서는 Nemotron-Personas를 **synthetic data / model training을 위한 seed**로 설명한다. long-context, tool-use, safety refusal, general chat 데이터를 만들기 위한 재료다. **검증된 인간 설문 응답 패널이 아니다.** 따라서 "persona에게 별점을 물어서 그 집단의 반응을 측정했다"고 주장하면 안 된다. 측정 대상은 **특정 LLM이 특정 persona conditioning에서 생성한 반응**이다.

### 7.2 feature 의존성: "가정하지 말 것"의 정확한 의미

Nemotron은 2단계에서 **PGM(Probabilistic Graphical Model)** 을 쓴다. 미국/한국 등의 census·행정 데이터로 age × education × occupation × marital status × geography 같은 **인구통계적 상관을 의도적으로 모델링**한다. NVIDIA 문서도 "naive independent sampling은 3살 외과의사 같은 nonsense를 만든다"고 말한다.

그래서 정확한 주의는 다음과 같다.

- **인구통계 feature를 독립이라고 가정하면 안 된다.** PGM이 이미 상관을 넣었다.
- **그렇다고 모든 feature의 joint distribution이 현실과 같다고 가정해도 안 된다.** PGM이 모델링하지 않은 상관, 표본 오차, 지역/버전 차이가 있다.
- **LLM이 생성한 서사형 필드(cultural_background, skills, hobbies, career_goals, persona)는 더 조심해야 한다.** 이들은 demographic/OCEAN seed에 조건화되어 LLM이 "그럴듯하게" 쓴 것이지, 실제 인간의 joint distribution에서 측정된 것이 아니다. 내적 일관성을 위해 오히려 **정형화(stereotype)된 조합**이 만들어진다.
- **데이터셋에 OCEAN이 들어있다고 가정하지 마라.** Korea 데이터셋 카드의 공개 컬럼에는 OCEAN 점수가 없다. 문서의 pipeline 설명과 실제 공개 스키마를 혼동하면 안 된다.
- **없는 조합을 임의로 만들지 마라.** 예: "19세, 은퇴, 서울, 전문직" 같은 조합을 feature를 따로 샘플링해 합성하면 PGM이 보장하지 않는 셀을 만들 수 있다. 가능하면 **실제 row를 조건화해 샘플링**하고, 셀별 n을 기록하라.
- **feature 중요도를 상관으로 추론하지 마라.** 별점과의 상관은 LLM의 prior/stereotype일 수 있다. 필요하면 feature masking/ablation으로 확인하라.

### 7.3 별점(rating) 측정의 함정

- **별점은 ordinal이다.** 1–5의 평균을 실수처럼 다루지 말고, 분포/중앙값/top-2-box를 보고하라. 평균이 필요하면 ordinal regression/beta regression을 고려하라.
- **LLM은 긍정 편향/중앙값 편향/아첨(sycophancy)을 보인다.** persona와 무관하게 4–5점에 몰릴 수 있다. "모르겠음/평가 불가" 옵션을 넣고, persona-swap과 no-persona baseline을 비교하라.
- **scale usage bias**: persona별로 점수 사용이 다를 수 있다. (예: 고연령 persona가 더 관대) 앵커 문항/비교 문항을 넣어라.
- **prompt/order effect**: topic을 먼저 보여주면 기대 점수를 추론한다. 순서를 랜덤화하고, 브랜드/정답 힌트를 제거하라.
- **일관성**: temperature 0만 쓰면 다양성이 사라지고, temperature를 높이면 분산이 커진다. 여러 seed × 여러 모델로 반복하고, 모델 버전을 기록하라.
- **unit of analysis**: persona 1개 = human 1명이 아니다. persona당 여러 번 샘플링하면 pseudo-replication이 된다. hierarchical/mixed-effects model로 persona와 prompt를 random effect로 두라.

### 7.4 표집(sampling)의 함정

- **목표 집단을 사후에 정의하지 마라.** 분석 전에 inclusion criteria와 비교 집단을 고정하라.
- **교차 셀의 n을 확인하라.** "20–29세 여성 서울 거주 마케팅 종사자" 같은 셀은 1M rows에서도 작을 수 있다.
- **가중치를 고려하라.** 목표 모집단과 데이터셋 분포가 다르면 raking/post-stratification으로 가중치를 주고, 가중치를 보고하라.
- **다중비교를 보정하라.** 여러 하위집단을 비교하면 우연한 차이가 나온다.
- **선택 편향**: 관심 있을 만한 persona만 골라 별점을 받으면 그건 target group의 반응이 아니라 **선택된 persona의 반응**이다.

### 7.5 타당도(validity) 검증

- **인간 benchmark와의 상관을 먼저 확인하라.** 같은 topic/문항을 실제 소규모 인간 집단(예: 30–50명)에게 물어 synthetic rating과의 상관/MAE를 계산하라. 상관이 낮으면 마케팅/정책 결론에 쓰면 안 된다.
- **known-groups test**: 실제로 차이가 알려진 두 집단/두 제품으로 synthetic panel이 그 차이를 재현하는지 확인하라.
- **persona fidelity test**: 같은 persona를 여러 번, persona를 바꿔가며, persona 없이 물어보라. persona 효과가 없으면 persona를 쓴 의미가 없다.
- **stereotype audit**: 특정 집단의 응답이 전형적 고정관념과 과도하게 일치하는지 검토하라. LLM은 내적 일관성을 위해 stereotype을 증폭할 수 있다.

### 7.6 윤리/법적 주의

- **synthetic임을 공개하라.** "실제 소비자 조사"라고 표기하면 안 된다.
- **민감한 의사결정에 쓰지 마라.** 채용, 신용, 의료, 보험 등 고위험 결정의 근거로 synthetic persona 반응을 쓰면 안 된다.
- **이름/지역/직업이 실제 개인과 겹칠 수 있다.** synthetic이지만 실제 사람으로 오인/재식별하지 않도록 주의하라.
- **라이선스**: Nemotron-Personas-Korea는 CC-BY-4.0 (dataset card 기준). 상업적 사용 시 attribution과 데이터셋 버전을 명시하라.

## 8. "persona + 별점" synthetic audience 프로토콜 (권장)

1. **연구 질문 고정**: "이 topic에 대한 target group의 반응 분포"인지, "persona별 반응 차이의 탐색"인지 먼저 정한다.
2. **target group 정의**: inclusion/exclusion 기준, 비교 집단, 표본 크기 목표를 사전 등록한다.
3. **persona 샘플링**: 실제 row에서 조건화해 샘플링. 셀별 n, 가중치, 데이터셋 버전을 기록한다.
4. **자극(stimulus) 설계**: topic 설명을 중립적으로 작성하고, 브랜드/기대 효과/정답 힌트를 제거한다.
5. **측정 도구**: 1–5 별점 + "모르겠음" + 이유 + 확신도. 가능하면 pairwise comparison/forced choice를 함께 쓴다.
6. **모델/실행**: 2개 이상 모델, temperature 0 + 0.7, 3–5 seeds. persona 유무 ablation 포함.
7. **인간 calibration**: 30–50명 인간 응답과 비교. 상관/MAE/순위 일치 확인.
8. **분석**: 분포, 중앙값, top-2-box, ordinal/hierarchical model, bootstrap CI. 평균만 보고하지 않는다.
9. **민감도 분석**: feature masking, 가중치 변경, 다른 모델, 다른 prompt.
10. **보고**: "synthetic persona simulation"임을 명시하고, human validation 결과와 한계를 함께 쓴다.

### 결과를 버려야 하는 신호

- persona를 바꿔도 별점 분포가 거의 같다. (persona가 작동하지 않음)
- 별점이 4–5에 포화된다. (변별력 없음)
- 인간 benchmark와의 상관이 낮다. (타당도 없음)
- 특정 셀 n이 5 미만이다. (불안정)
- 모델 버전/prompt/seed에 따라 결론이 뒤집힌다. (취약)
- 결과가 고정관념과 지나치게 일치한다. (stereotype amplification 의심)

## 9. 타당성 확보 방법론 — Calibrated Hybrid

### 9.1 냉정한 출발점

- **synthetic alone은 시장/정책 결정에 쓸 수 없다.** Pew Research Center(2026)는 digital twin + extended profile + expert reflection + Claude Opus 4.6으로 미국 ATP 3개 wave를 재현했는데, 인간-합성 평균 절대오차가 **약 12%p**였다. 하위집단은 12–16%p, Hispanic World Cup 관심은 합성 97% vs 실제 42%였다. 즉 "그럴듯한" 결과가 "타당한" 결과는 아니다.
- **synthesis alone은 편향이 크다.** Krsteski et al.(ACL 2026)은 synthesis alone의 편향이 **24–86%**였고, **rectification**을 결합하면 **5% 미만**으로 줄고 유효 표본이 최대 **14%** 증가한다고 보고한다. 핵심은 "인간 응답을 어디에 쓸 것인가"다. 모두 fine-tuning에 쓰지 말고, **대부분을 rectification에 배분**하라.
- **타당성은 "확보"하는 것이 아니라 "가정 + 보정 + 불확실성"으로 관리하는 것**이다. 최종 추정치는 반드시 확률표본(또는 대표성 있는 인간 앵커)에 닻을 내려야 한다.

### 9.2 Calibrated Hybrid pipeline (Anchor → Simulate → Rectify → Validate)

```
[1] Estimand 정의
    - target population, subgroup, outcome (mean/share/WTP/policy support)
    - decision threshold, 허용 오차
        ↓
[2] Human anchor
    - 확률표본 또는 대표성 있는 human sample (n=100–300+)
    - 같은 문항/같은 자극으로 측정
        ↓
[3] Synthetic sample
    - persona-conditioned LLM/digital twin (N=5k–50k)
    - 2+ models, 3–5 seeds, temperature 0 & 0.7
        ↓
[4] Rectification / calibration
    - human anchor에서 bias를 추정해 synthetic estimate 보정
    - PPI, regression calibration, isotonic, post-stratification
        ↓
[5] Validation
    - predictive / distributional / substantive validity
    - holdout human sample, known-groups, coverage
        ↓
[6] Decision
    - bias-corrected estimate + 95% CI
    - CI가 decision threshold를 넘지 못하면 human data 추가
```

### 9.3 Prediction-Powered Inference (PPI)

인간 라벨이 적을 때 synthetic/ML 예측을 결합해 **유효한 신뢰구간**을 얻는 방법이다.

- 전체 synthetic 표본 \(N\)에 대한 예측 \(f(X_i)\)
- 인간 앵커 표본 \(n\)에 대한 실제 라벨 \(Y_i\)
- PPI estimator:

\[
\hat{\theta}_{PPI} = \frac{1}{N}\sum_{i=1}^{N} f(X_i) + \frac{1}{n}\sum_{i=1}^{n}\left(Y_i - f(X_i)\right)
\]

- 앞항은 synthetic 평균, 뒤항은 human anchor에서의 **bias correction**이다. synthetic이 편향되어 있어도 human anchor가 있으면 보정된다.
- PPI는 mean, quantile, regression coefficient 등으로 확장된다. 신뢰구간은 human anchor의 불확실성을 반영한다.
- **중요:** synthetic 표본이 target population과 같은 분포가 아니면 PPI만으로는 부족하다. **post-stratification/raking**으로 target population에 맞춰야 한다.

### 9.4 Rectification: human label을 어디에 쓸 것인가

Krsteski et al.(2026)의 핵심:

- human label을 모두 fine-tuning에 쓰면 rectification에 쓸 표본이 줄어든다.
- **대부분을 rectification에 배분**하고, fine-tuning은 소량만.
- rectification은 synthetic estimate의 **population-level bias**를 보정한다.
- 결과: bias <5%, effective sample size +14% (그들의 실험 기준).

실무적으로는:

1. human anchor를 **calibration set**과 **validation set**으로 나눈다.
2. calibration set에서 synthetic-human 차이를 추정한다. (mean bias, subgroup bias, scale bias)
3. validation set에서 보정 후 성능을 확인한다. (bias, RMSE, coverage)
4. subgroup별 bias가 다르면 **group-specific calibration**을 한다. (단, 셀별 n 확보)

### 9.5 시장규모(market size)에 쓰려면

시장규모는 "설문 평균"이 아니라 **인구 × 발생률 × 채택률 × 가격**의 곱이다. synthetic persona 별점만으로 TAM/SAM/SOM을 추정하면 안 된다.

권장:

- **Bottom-up TAM/SAM/SOM**:
  - TAM = target population × category incidence × annual spend
  - SAM = TAM × serviceable geography/channel/price
  - SOM = SAM × realistic adoption (analog products, pre-orders, waitlist, conjoint)
- **Conjoint/choice experiment**는 인간 표본으로 추정한다. synthetic은 attribute/level pretest와 가설 생성에 쓴다.
- synthetic으로 segment **상대** 선호를 추정하고, human anchor로 **절대** 수준을 보정한다.
- **Bayesian updating**: synthetic prior + human likelihood → posterior. 의사결정은 posterior의 lower bound로.
- **Value of Information**: human data를 더 모을 가치가 있는지 계산한다.

### 9.6 정책(policy)에 쓰려면

- 정책 결정은 **대표성 있는 인간 조사 + 인과설계**가 필요하다. synthetic은 다음에 쓴다:
  - 메시지/프레임 pretest
  - 이질적 효과(heterogeneous treatment effect) 가설 생성
  - stakeholder/이해관계자 매핑
  - 설문 문항/선택지 pre-test
- 최종 정책 추정에는 **MRP(multilevel regression and post-stratification)**, **small-area estimation**, **PPI**를 사용하되, human survey를 anchor로 둔다.
- **분배적 영향**은 실제 microdata가 필요하다. synthetic persona로 대체하지 마라.
- **deliberative polling**/공론조사는 인간 참여가 필수다. synthetic은 사전 시나리오 생성에만.

### 9.7 검증 지표와 의사결정 규칙

| 차원 | 지표 | 통과 기준(예시) |
|---|---|---|
| Predictive | RMSE, Pearson r, MAE | human holdout에서 r > 0.5, MAE < 0.5 scale point |
| Distributional | mean bias, SD ratio, KS, Wasserstein | mean bias < 0.2 SD, SD ratio 0.8–1.2 |
| Substantive | subgroup ordering, regression coefficients, predictor ranking | 주요 subgroup ordering 일치, coefficient sign 일치 |
| Calibration | PPI/rectified CI coverage | 95% CI coverage ≥ 90% (simulation) |
| Robustness | model/seed/prompt variation | 결론이 뒤집히지 않음 |

**의사결정 규칙:** bias-corrected 95% CI의 lower bound가 decision threshold를 넘지 못하면, 결론을 내리지 말고 human data를 추가한다. "점추정이 threshold를 넘었다"는 이유로 결정하면 안 된다.

### 9.8 최소 프로토콜 (별점 시뮬레이션)

1. target population과 estimand를 고정한다. (예: "서울 20–39세 여성의 이 교육 프로그램 추천 의향 평균")
2. human anchor 100–300명을 모집한다. 같은 자극, 같은 별점, 같은 covariate.
3. synthetic 5k–50k를 2개 모델 × 3 seeds로 생성한다.
4. calibration set/validation set으로 human anchor를 나눈다.
5. **PPI + post-stratification**으로 bias-corrected estimate와 95% CI를 계산한다.
6. subgroup은 cell n≥30을 확보한 것만 보고한다.
7. synthetic-human 상관이 낮거나 CI가 너무 넓으면, **"탐색적"**으로만 보고한다.
8. 결과 보고서에 **synthetic 비율, human anchor 크기, calibration 방법, coverage, 한계**를 명시한다.

### 9.9 참고 문헌

- Pew Research Center (2026). *Can AI Stand In for Human Survey-Takers? Not Really.* https://www.pewresearch.org/data-labs/2026/09/30/can-ai-stand-in-for-human-survey-takers-not-really/
- Pew Research Center (2026). *Methodology: Silicon Samples.* https://www.pewresearch.org/data-labs/2026/09/30/methodology-silicon-samples/
- Krsteski, Russo, Chang, West, Gligorić (2026). *Valid Survey Simulations with Limited Human Data: The Roles of Prompting, Fine-Tuning, and Rectification.* ACL 2026. https://arxiv.org/abs/2510.11408
- D’Ecclesiis, Castellacci, Ahmadi (2026). *Validating LLM-Generated Synthetic Survey Samples: A Use-Dependent Multi-Dimensional Framework.* https://arxiv.org/abs/2611.00256
- Angelopoulos et al. (2023). *Prediction-Powered Inference.* Science. https://arxiv.org/abs/2301.09633
- Argyle et al. (2023). *Out of One, Many: Using Language Models to Simulate Human Samples.* Political Analysis.

## 10. 라이선스 주의

- Nemotron-Personas: 데이터셋별 카드 확인 (상업적 사용 가능으로 홍보되는 버전 있음).
- PersonaFeedback: CC BY 4.0 (arXiv 기준).
- PERSONA: CC BY 4.0.
- PersonaHub / SCOPE / PersonaGym: arXiv 라이선스 기준 CC BY-NC-SA 4.0 (연구/비상업 중심). 상업 서비스 적용 전 원 라이선스 확인 필요.
