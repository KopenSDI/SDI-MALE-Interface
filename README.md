# SDI ↔ ETRI 연동 인터페이스 & MALE 사용 가이드

> **목적** — ETRI(IaC Provider)와 KETI(SDI Orchestration)의 **연동 경계와 계약(interface contract)** 을 정의하고, 전달된 워크로드에서 **MALE(A‑L‑E)이 어떻게 사용되는지**를 설명한다.
> 본 저장소는 ETRI 공유용이며, KETI 내부 구현 세부는 제외하고 **경계(API Server)와 규격**에 집중한다.

이 문서는 협의자료(슬라이드 2 "MALE 기반 오케스트레이션 동작 구조도")의 **후속 상세 설명**으로 작성되었다.

---

## 1. 연동 경계 (한눈에)

```
[ ETRI ]                              │                 [ KETI / OpenSDI ]
                                      │
 IaC Provider (LLM 기반 YAML 생성) ───┼──▶  API Server ──▶ MALE Operator ──▶ Analysis Engine ──▶ Scheduler ──▶ (Edge) Migration
                                      │    (Manifest Bridge)   (CRD/Webhook)     (A‑L‑E 점수)      (Node 선택)
                                      │
                         ★ 협의 경계선 ★          └──────────────── KETI 내부 구현 (협의 불필요) ────────────────┘
```

- **ETRI가 책임지는 것**: 요구사항을 담은 **워크로드 선언(YAML/CR)** 을 KETI 규격에 맞게 생성하고 전달.
- **KETI가 책임지는 것**: 전달받은 선언을 기반으로 **MALE 반영 → 스케줄링 → 오케스트레이션** 수행.
- **공동 협의 대상**: 경계에서 오가는 **① 전달 방식 ② CR/Argument 스키마와 값 의미**. (그 뒤 모듈의 동작 원리는 KETI 내부 사항)

---

## 2. 문서 구성

| 문서 | 내용 |
| --- | --- |
| [`docs/01-orchestration-flow.md`](docs/01-orchestration-flow.md) | **★ 슬라이드 2 후속 설명** — MALE 기반 오케스트레이션 전체 흐름과 각 단계에서 MALE이 사용되는 방식 |
| [`docs/02-etri-boundary.md`](docs/02-etri-boundary.md) | ETRI↔KETI 연동 경계, 전달 방식(GitOps/HTTP), ETRI 산출물 정의 |
| [`docs/03-cr-argument-schema.md`](docs/03-cr-argument-schema.md) | **계약** — `MaleWorkload` CR / `male.keti.dev/*` 주석 스키마 (필드·의미·예시) |
| [`docs/04-open-issues.md`](docs/04-open-issues.md) | 협의가 필요한 미결 항목 (네이밍·값 의미·전달채널 등) |
| [`examples/`](examples/) | 미션별 예시 워크로드 (자율주행 / 객체탐지 / 내비게이션) |

## 2.1 코드 구성 (`src/`, `crds/`)

MALE이 실제로 어떻게 소비·반영되는지 확인할 수 있는 참조 구현(KETI). *vendor·가상환경·시크릿은 제외, InfluxDB 토큰 등은 환경변수로 정화됨.*

| 경로 | 내용 | 슬라이드 2 단계 |
| --- | --- | --- |
| [`src/api-server/`](src/api-server/) | **경계 모듈** — `sdi_manifest_bridge` (요구사항 보강·검증·apply) | ① 선언 전달 |
| [`src/male-operator/`](src/male-operator/) | **MALE Operator** — CRD 타입(`maleworkload_types.go`), 컨트롤러(reconcile), **Mutating Webhook**(중요도 재정의·MALEpatch) | ②③⑤ |
| [`src/analysis-engine/`](src/analysis-engine/) | **Analysis Engine** — `ALE_Weight_Manager`(A‑L‑E 점수·가중합), 스코어링 로직 | ④ 점수 산출 |
| [`crds/`](crds/) | `MaleWorkload` / `MalePolicy` CRD 정의(YAML) — 계약 스키마 | ② |

> 각 모듈이 슬라이드 2의 어느 단계에 해당하는지는 [`docs/01-orchestration-flow.md`](docs/01-orchestration-flow.md) 참조.
> 코드 내 InfluxDB 접속 정보는 `INFLUX_TOKEN`, `INFLUX_URL` 환경변수로 주입한다(하드코딩 제거됨).

---

## 3. MALE 요약 (A‑L‑E)

MALE = **M**ission + **A**ccuracy · **L**atency · **E**nergy. 워크로드가 무엇을 더 중시하는지를 **0~1 가중치**로 표현한다.

| 미션 | Accuracy | Latency | Energy | 성격 |
| --- | --- | --- | --- | --- |
| Autonomous Driving | 0.6 | 0.3 | 0.1 | 정확도 우선 |
| Object Detection | 0.3 | 0.5 | 0.2 | 지연 우선 |
| Navigation | 0.4 | 0.5 | 0.1 | 지연·정확도 균형 |

이 값이 KETI 오케스트레이션에서 **혼합 중요도(Mixed‑Criticality) 재정의 → 노드 선택(A‑L‑E affinity)** 의 기준이 된다. 자세한 흐름은 [`docs/01-orchestration-flow.md`](docs/01-orchestration-flow.md) 참고.

---

## 4. 빠른 예시

ETRI가 생성해 전달하는 선언의 최소 형태(자율주행):

```yaml
apiVersion: male.keti.dev/v1alpha1
kind: MaleWorkload
metadata:
  name: autonomous-vehicle
  namespace: male-test
spec:
  targetRef:                 # 이 MALE 요구사항이 적용될 워크로드
    apiVersion: apps/v1
    kind: Deployment
    name: autonomous-vehicle
  mission: "autonomous-vehicle-perception"
  importance:                # A-L-E 가중치 (합계 1 권장)
    accuracy: 0.6
    latency: 0.3
    energy: 0.1
  allowPolicyOverride: true  # KETI 정책엔진의 중요도 재정의 허용
```

전체 예시는 [`examples/`](examples/) 참고.
