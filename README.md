# SDI ↔ ETRI 연동 인터페이스 / MALE 사용 안내

ETRI(IaC Provider)와 KETI(SDI Orchestration)가 워크로드를 주고받는 방식, 그리고 전달된 워크로드에서 MALE(A‑L‑E)이 실제로 어떻게 쓰이는지를 정리한 저장소입니다. 이 저장소만 읽어도 내용이 이해되도록 작성했습니다.

## 연동 구조

ETRI가 워크로드 선언(YAML/CR)을 만들어 KETI에 넘기면, KETI가 그것을 받아 MALE를 반영하고 스케줄링·운영합니다. 두 기관의 경계는 KETI의 **API Server** 입니다.

```
        ETRI                              KETI
  IaC Provider  ──워크로드 선언──▶  API Server ──▶ MALE Operator ──▶ Analysis Engine ──▶ Scheduler ──▶ 운영
 (YAML/CR 생성)                     (받는 지점)
```

역할은 이렇게 나뉩니다.

- **ETRI** : 요구사항을 담은 워크로드 선언을 만들어 전달
- **KETI** : 받은 선언으로 MALE 반영, 스케줄링, 운영
- **함께 정할 것** : 전달 방식, 그리고 선언에 담는 필드(스키마)와 값의 의미

API Server 뒤쪽(스케줄러가 노드를 어떻게 고르는지 등)은 KETI 내부 구현이라 ETRI가 자세히 알 필요는 없습니다. 다만 "MALE 값을 넣으면 무슨 일이 일어나는지"는 [docs/01](docs/01-orchestration-flow.md)에 순서대로 설명해 두었습니다.

## 문서

- [docs/01-orchestration-flow.md](docs/01-orchestration-flow.md) — 워크로드가 배포되어 운영되기까지의 흐름과, 각 단계에서 MALE이 쓰이는 방식
- [docs/02-etri-boundary.md](docs/02-etri-boundary.md) — 연동 경계(API Server)와 전달 방식
- [docs/03-cr-argument-schema.md](docs/03-cr-argument-schema.md) — 전달하는 선언의 필드 규격 (MaleWorkload CR, 주석)
- [examples/](examples/) — 미션별 예시 워크로드

## 코드 (`src/`, `crds/`)

MALE이 실제로 어떻게 처리되는지 확인할 수 있는 KETI 참조 구현입니다. vendor·가상환경·시크릿은 제외했고, InfluxDB 토큰 같은 접속 정보는 환경변수로 바꿔 두었습니다.

- `src/api-server` — 워크로드 선언을 받아 보강·검증한 뒤 클러스터에 적용 (`sdi_manifest_bridge`)
- `src/male-operator` — MALE 요구사항을 CR로 관리하고, 중요도를 재정의하고, 워크로드에 주입하는 오퍼레이터
- `src/analysis-engine` — A‑L‑E 점수를 계산하는 로직 (`ALE_Weight_Manager` 등)
- `crds` — `MaleWorkload` / `MalePolicy` CRD 정의

## MALE이란

Mission과 Accuracy·Latency·Energy의 앞글자입니다. 워크로드가 무엇을 더 중요하게 여기는지를 0~1 가중치로 나타냅니다.

| 미션 | Accuracy | Latency | Energy | 성격 |
| --- | --- | --- | --- | --- |
| 자율주행 (Autonomous Driving) | 0.6 | 0.3 | 0.1 | 정확도 우선 |
| 객체탐지 (Object Detection) | 0.3 | 0.5 | 0.2 | 지연 우선 |
| 내비게이션 (Navigation) | 0.4 | 0.5 | 0.1 | 지연·정확도 균형 |

이 값이 KETI 쪽에서 워크로드의 중요도를 판정하고 노드를 고르는 기준이 됩니다.

## 예시

자율주행 워크로드에 붙이는 최소 선언:

```yaml
apiVersion: male.keti.dev/v1alpha1
kind: MaleWorkload
metadata:
  name: autonomous-vehicle
  namespace: male-test
spec:
  targetRef:                 # 이 요구사항을 적용할 워크로드
    apiVersion: apps/v1
    kind: Deployment
    name: autonomous-vehicle
  mission: "autonomous-vehicle-perception"
  importance:                # A-L-E 가중치 (합계 1 권장)
    accuracy: 0.6
    latency: 0.3
    energy: 0.1
  allowPolicyOverride: true  # KETI가 중요도를 재정의하도록 허용
```

나머지 예시는 [examples/](examples/)를 참고하세요.
