# MALE 기반 오케스트레이션 동작 흐름

ETRI가 만든 워크로드 선언이 KETI에 전달된 뒤, MALE(A‑L‑E)이 반영되어 스케줄링·운영되기까지의 순서를 정리한다. 각 단계에서 MALE 값이 어떻게 쓰이는지에 초점을 둔다.

전체 순서:

```
1. 선언 전달      2. CR 등록        3. 중요도 판정      4. 점수 계산        5. 워크로드 주입     6. 스케줄링      7. 운영
  ETRI       →  MALE Operator  →  MALE Operator  →  Analysis Engine  →  MALE Operator   →  Scheduler   →  Migration 등
 (API Server 경유)
```

> 참고: 여기서 "MALE Operator"는 Kubernetes Operator다. CRD(`MaleWorkload`/`MalePolicy`) + Reconcile 컨트롤러 + Mutating Webhook로 구성되며, API 그룹은 `male.keti.dev/v1alpha1`. MALE 요구사항의 등록·중요도 재정의·워크로드 주입을 담당한다.

---

## 1. 워크로드 선언 전달 (ETRI → API Server)

ETRI가 워크로드(Deployment/Pod)와 MALE 요구사항을 담은 선언을 만들어 KETI에 넘긴다. MALE 요구사항은 `MaleWorkload` CR로 주거나, 파드에 `male.keti.dev/*` 주석으로 직접 붙일 수 있다. 전달은 GitOps(Argo CD)나 HTTP로 한다([docs/02](02-etri-boundary.md) 참고).

이 단계가 **ETRI가 A‑L‑E 가중치와 미션 정보를 시스템에 넣는 유일한 지점**이다. 이후 단계는 모두 KETI가 이 값을 활용하는 과정이다.

## 2. CR 등록 (API Server → MALE Operator)

전달된 선언이 클러스터에 적용되면, MALE Operator가 이를 `MaleWorkload`(정책은 `MalePolicy`) CR로 저장한다. 이렇게 등록된 CR이 이후 단계들이 참조하는 요구사항의 기준점이 된다.

## 3. 중요도 판정 (MALE Operator)

MALE Operator가 A‑L‑E 값을 보고 워크로드의 **혼합 중요도(Mixed‑Criticality)** 를 정한다. 사용자가 준 등급을 그대로 쓰지 않고, A‑L‑E 패턴에 따라 재정의할 수 있다.

예를 들어 정확도와 지연이 모두 높게 요구되는 자율주행 워크로드(`accuracy ≥ 0.6` 이고 `latency ≥ 0.3`)는, 사용자가 낮은 등급으로 냈더라도 **안전 필수(Safety‑Critical)** 등급으로 올린다. 이 등급이 스케줄링 우선순위와 자원 보장에 반영된다.

## 4. 점수 계산 (Analysis Engine)

Analysis Engine이 노드/디바이스별로 A‑L‑E 점수(0~100)를 계산한다.

- Accuracy: 모델·하드웨어 성능
- Latency: 위치 근접성(locality)·응답시간
- Energy: 전력/배터리 여유

여기서 ETRI가 준 **가중치**와 KETI가 측정한 **점수**가 합쳐져 `가중 점수 = Σ(점수 × 가중치)` 형태로 계산된다. 실측 데이터가 아직 없으면 중립값으로 대체한다(측정·수집은 KETI 몫이라 ETRI가 신경 쓸 부분은 아니다).

## 5. 워크로드 주입 (MALE Operator, Mutating Webhook)

MALE Operator의 Mutating Webhook이 워크로드가 실제로 만들어질 때, 계산된 점수·중요도·스케줄링 힌트를 파드 스펙에 주석/환경변수로 끼워 넣는다. 이 과정을 거쳐야 스케줄러와 런타임이 MALE 정보를 인식할 수 있다.

## 6. 스케줄링 (SDI Scheduler)

커스텀 스케줄러가 MALE 점수를 기준으로 노드를 고른다. 대략 다음 순서다.

1. MALE 점수 산출
2. 후보 필터링 (Cloud / Edge / Device 중 어디에 둘지)
3. 재점수 (모니터링 데이터가 있으면 반영)
4. 최종 노드 선택 — Accuracy는 고성능 노드, Latency는 근거리 노드, Energy는 전력 여유 노드로 향하게

정확도 우선 워크로드는 성능 좋은 노드로, 지연 우선 워크로드는 가까운 노드로 배치되는 식이다.

## 7. 운영 (Migration 등)

배치된 뒤에도 리소스 압박이나 중요도 변화에 따라 워크로드를 다른 노드로 옮기는(마이그레이션) 등의 운영이 이어진다. 이때도 중요도와 리소스 상태가 판단 근거가 된다.

---

## 요약: MALE은 어디서 어떻게 쓰이나

| 단계 | MALE의 사용 |
| --- | --- |
| 1. 선언 전달 | ETRI가 A‑L‑E 가중치 + 미션을 선언에 담아 넣음 |
| 2. CR 등록 | A‑L‑E가 `MaleWorkload` CR로 저장됨 |
| 3. 중요도 판정 | A‑L‑E 패턴 → 중요도 등급으로 변환 |
| 4. 점수 계산 | 가중치 × 측정 점수 = 가중 점수 |
| 5. 주입 | 점수·중요도를 파드에 삽입 |
| 6. 스케줄링 | A‑L‑E 기준으로 노드 선택 |
| 7. 운영 | 중요도 기반 재배치 |

**ETRI가 직접 관여하는 범위는 1~2단계(무엇을 어떤 형식으로 넣는가)까지다.** 3단계 이후는 KETI가 그 값을 어떻게 활용하는지에 대한 참고 설명이다.

---

## (부록) 협의자료 시퀀스 다이어그램과의 대응

협의자료의 시퀀스 다이어그램을 함께 보는 경우, 위 단계와 다이어그램의 메시지는 다음과 같이 대응한다. (다이어그램이 없어도 위 본문만으로 이해된다.)

| 본 문서 단계 | 시퀀스 다이어그램 메시지 |
| --- | --- |
| 1. 선언 전달 | `applyK8sYaml` |
| 2. CR 등록 | `persistMALE` / `registerCRD` / `createCRInstance` |
| 3. 중요도 판정 | `decideALE` / `sendMixedCriticality` |
| 4. 점수 계산 | `getALEweight` / `pullAnalysisResult` |
| 5. 워크로드 주입 | `MALEpatch` |
| 6. 스케줄링 | `schedule` / NodeSelect |
| 7. 운영 | `par [Migration] / [Autoscaling]` |
