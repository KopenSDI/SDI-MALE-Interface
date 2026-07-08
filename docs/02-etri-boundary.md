# ETRI ↔ KETI 연동 경계

## 1. 경계는 어디인가 — **API Server (SDI Manifest Bridge)**

ETRI와 KETI의 협의 경계는 **API Server 입력 지점**이다. 그 뒤(MALE Operator·Analysis Engine·Scheduler·Migration)는 KETI 내부 구현이다.

```
ETRI 산출물 ──(전달)──▶ [API Server] ──▶ (이후 KETI 내부)
   YAML/CR              입력 계약 지점
```

| 구분 | 담당 | 협의 필요 |
| --- | --- | --- |
| 워크로드 선언 생성 (LLM) | ETRI | — |
| **전달 방식** | 공동 | ✅ |
| **CR/Argument 스키마·값 의미** | 공동 | ✅ |
| MALE Operator 내부 처리 | KETI | ❌ |
| 점수 산출 / 노드 선택 / 마이그레이션 | KETI | ❌ (개념 공유만) |

## 2. ETRI 산출물 (무엇을 만드는가)

ETRI는 LLM으로 다음을 생성한다:

1. **워크로드 리소스** — `Deployment` 또는 `Pod`
2. **MALE 요구사항** — 아래 둘 중 하나
   - **(권장)** `MaleWorkload` CR — 워크로드와 분리된 선언 → [03-cr-argument-schema](03-cr-argument-schema.md)
   - **(간이)** 파드 라벨/주석에 `male.keti.dev/{accuracy,latency,energy}` 직접 부착

## 3. 전달 방식 (Transport) — 협의 항목

| 방식 | 설명 | 상태 |
| --- | --- | --- |
| **GitOps (Argo CD)** | ETRI가 Git 리포에 YAML push → Argo CD Agent가 클러스터에 자동 동기화 | 슬라이드 6 기준 유력안 |
| **HTTP (API Server)** | ETRI가 API Server 엔드포인트로 직접 POST | 대안 |

> 슬라이드 6: *"오케스트레이션 내 Git 변경 감지 Agent 배포(Argo CD) → GitOps"* 로 가닥. 최종 채널 확정은 협의 필요.

## 4. 핵심 원칙

> ETRI는 **"무엇을(스키마) · 어떻게(전달채널) 넘길지"** 까지만 확정하면 된다.
> KETI가 그 값으로 **"무엇을 하는지(중요도 재정의·점수·스케줄·마이그레이션)"** 는 내부 구현이며, [01-orchestration-flow](01-orchestration-flow.md)의 개념 설명으로 충분하다.
