# MALE 기반 오케스트레이션 동작 흐름 (슬라이드 2 상세 설명)

> 본 문서는 협의자료 슬라이드 2 *"MALE 기반 오케스트레이션 동작 구조도(UML Sequence)"* 의 후속 설명이다.
> 각 단계에서 **MALE(A‑L‑E)이 어떻게 소비·반영되는지**를 중심으로 기술한다.

---

## 전체 파이프라인

```
① 선언 전달        ② CRD 등록         ③ 중요도 재정의       ④ 점수 산출        ⑤ 워크로드 패치      ⑥ 스케줄링          ⑦ 운영(Edge)
IaC Provider ──▶ API Server ──▶ MALE Operator ──▶ Analysis Engine ──▶ MALE Operator ──▶ Scheduler ──▶ Migration
 (ETRI)          applyK8sYaml     persistMALE       getALEweight         MALEpatch          schedule       (SDx)
                                  createCRInstance   decideALE            (webhook)          NodeSelect
```

각 단계와 MALE의 역할은 다음과 같다.

---

## ① 선언 전달 — `applyK8sYaml` (ETRI → API Server)

- **주체**: ETRI(IaC Provider). LLM으로 워크로드 YAML을 생성.
- **내용**: 워크로드(Deployment/Pod) + **MALE 요구사항**(`MaleWorkload` CR 또는 `male.keti.dev/*` 주석).
- **전달**: GitOps(Argo CD) 또는 HTTP(API Server). → [02-etri-boundary](02-etri-boundary.md)
- **MALE 관점**: 이 단계에서 A‑L‑E 가중치(`importance.accuracy/latency/energy`)와 미션이 **최초로 시스템에 진입**한다. **여기가 ETRI가 MALE 값을 넣는 유일한 지점**이다.

## ② CRD 등록 — `persistMALE` / `registerCRD` / `createCRInstance` (API Server → MALE Operator)

> **MALE Operator** = 슬라이드 2의 MALE 관리 모듈. Kubernetes Operator(Kubebuilder)로서 **CRD(`MaleWorkload`/`MalePolicy`) + Reconcile 컨트롤러 + Mutating Webhook** 로 구성된다. (CR API 그룹: `male.keti.dev/v1alpha1`) — MALE 요구사항의 **등록·중요도 재정의·워크로드 주입(patch)** 을 담당한다.

- 전달된 선언이 클러스터에 적용되면, KETI의 **MALE Operator**가 `MaleWorkload`(그리고 정책은 `MalePolicy`) **CR 인스턴스**로 저장한다.
- **MALE 관점**: A‑L‑E 값이 쿠버네티스 **CustomResource로 영속화**되어, 이후 단계들이 참조할 수 있는 "요구사항의 단일 출처(source of truth)"가 된다.

## ③ 중요도 재정의 — `decideALE` / Mixed‑Criticality (MALE Operator)

- MALE Operator가 A‑L‑E 패턴을 보고 **혼합 중요도(Mixed‑Criticality)** 를 재정의한다.
- **실제 규칙 예시**(자율주행): `A ≥ 0.6 && L ≥ 0.3` → 사용자가 준 중요도 `A(Best‑Effort)`를 **`C(Safety‑Critical)`로 승격**.
- **MALE 관점**: A‑L‑E 가중치가 **정적인 숫자에서 → 운영 정책(중요도 등급)으로 변환**되는 핵심 단계. 이 등급이 스케줄링 우선순위·자원 보장에 영향.

## ④ 점수 산출 — `getALEweight` / `pullAnalysisResult` (Scheduler ↔ Analysis Engine)

- **Analysis Engine(MALE Profiler)** 이 디바이스/노드별 **A‑L‑E 점수(0~100)** 를 계산한다.
  - Accuracy: 모델·HW 성능 기반, Latency: 지역성(locality)·응답시간 기반, Energy: 전력/배터리 기반.
- 스케줄러가 `getALEweight` 로 이 점수를 조회한다.
- **MALE 관점**: ETRI가 준 **가중치(중요도)** 와 KETI가 측정한 **점수(성능)** 가 결합되어 `weighted_score = Σ(score × weight)` 형태의 **가중 점수**로 산출된다.

> 참고: 실측 A/L/E 데이터를 수집하는 파이프라인은 KETI 내부 사항이며, 데이터가 없을 때는 중립값으로 폴백한다. ETRI는 값을 넣기만 하면 되고, 측정·점수화는 KETI가 담당.

## ⑤ 워크로드 패치 — `MALEpatch` (MALE Operator, Mutating Webhook)

- MALE Operator의 **Mutating Admission Webhook** 이 워크로드에 A‑L‑E 점수/중요도/스케줄링 힌트를 **주석·환경변수로 주입**한다.
- **MALE 관점**: A‑L‑E 정보가 **실제 파드 스펙에 반영**되어 스케줄러·런타임이 인식할 수 있는 형태가 된다.

## ⑥ 스케줄링 — `schedule` / `NodeSelect` (SDI Scheduler)

- 커스텀 스케줄러(`sdi-scheduler`, intent‑driven 플러그인)가 **MALE Score 기반 노드 선택**을 수행:
  1. **MALE Score** 산출
  2. **Filtering** (Cloud / Edge / Device 후보 필터)
  3. **Re‑Scoring** (모니터링 데이터 반영, 선택)
  4. **NodeSelect Algorithm**
     - Accuracy → HW performance
     - Latency → Locality Affinity
     - Energy → Power Budget Affinity
- **MALE 관점**: A‑L‑E 가중치가 **최종 배치(노드 선택)** 를 결정한다. 정확도 우선 워크로드는 고성능 노드로, 지연 우선 워크로드는 근거리(zone/region) 노드로 향한다.

## ⑦ 운영 — `par [Migration] / [Autoscaling]` (SDx Manager, Edge)

- 배치 후 운영 단계에서 리소스 압박/중요도 변화에 따라 **마이그레이션**(체크포인팅 기반 무중단 이전) 등이 수행된다.
- **MALE 관점**: 중요도(criticality)와 리소스 상태를 근거로 **동적 재배치**가 일어난다. (오토스케일링 연동은 확장 예정 영역)

---

## 요약: "MALE는 어디서, 어떻게 쓰이나"

| 단계 | MALE의 사용 방식 |
| --- | --- |
| ① 전달 | ETRI가 A‑L‑E 가중치 + 미션을 선언에 담아 주입 |
| ② CRD | A‑L‑E가 `MaleWorkload` CR로 영속화 |
| ③ 재정의 | A‑L‑E 패턴 → 혼합 중요도(등급)로 변환 |
| ④ 점수 | 가중치 × 측정 점수 = 가중 점수 |
| ⑤ 패치 | 파드에 점수/중요도 주입 |
| ⑥ 스케줄 | A‑L‑E → 노드 선택(성능/지역성/전력) |
| ⑦ 운영 | 중요도 기반 재배치 |

> **ETRI가 알아야 할 범위**: ①~② (무엇을 어떤 스키마로 넣는가). ③~⑦은 KETI가 그 값을 **어떻게 활용하는지**에 대한 참고 설명이다.
