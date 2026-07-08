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

## 3. 전달 방식 (Transport)

**현재는 HTTP(API Server)로 연동하고, 추후 GitOps(Argo CD) 연동으로 전환**한다. (GitOps는 ETRI가 담당)

| 단계 | 방식 | 설명 |
| --- | --- | --- |
| **현재** | **HTTP (API Server)** | ETRI가 API Server 엔드포인트로 JSON POST |
| **향후** | **GitOps (Argo CD)** | ETRI가 Git 리포에 매니페스트 push → Argo CD가 클러스터에 자동 동기화 |

## 4. 핵심 원칙

> ETRI는 **"무엇을(스키마) · 어떻게(전달채널) 넘길지"** 까지만 확정하면 된다.
> KETI가 그 값으로 **"무엇을 하는지(중요도 재정의·점수·스케줄·마이그레이션)"** 는 내부 구현이며, [01-orchestration-flow](01-orchestration-flow.md)의 개념 설명으로 충분하다.
