# CR / Argument 스키마 (연동 계약)

> ETRI가 생성·전달하는 선언의 **필드 규격**. 실제 구현(`male-operator`)의 CRD를 기준으로 작성.

## 1. `MaleWorkload` CR (권장 방식)

```yaml
apiVersion: male.keti.dev/v1alpha1
kind: MaleWorkload
metadata:
  name: <workload-name>
  namespace: <namespace>
spec:
  targetRef:                    # 이 요구사항이 적용될 대상 워크로드
    apiVersion: apps/v1
    kind: Deployment            # 또는 Pod
    name: <workload-name>
  mission: "<mission-string>"   # 미션 식별자
  importance:                   # ★ A-L-E 가중치 (각 0~1, 합계 1 권장)
    accuracy: 0.6
    latency: 0.3
    energy: 0.1
  mcSpec:                       # 혼합 중요도 / 실시간 파라미터 (선택)
    criticality: "A"            # 사용자 지정 중요도 (KETI가 재정의할 수 있음)
    rtPeriod: 100               # 실시간 주기 (ms)
    rtWcet: 30                  # 최악수행시간 WCET (ms)
    rtDeadline: 100             # 데드라인 (ms)
    missionId: "av-mission-1"
  allowPolicyOverride: true     # KETI 정책엔진의 중요도 재정의 허용 여부
```

### 필드 설명

| 필드 | 타입 | 의미 |
| --- | --- | --- |
| `targetRef` | object | MALE 요구사항을 적용할 워크로드 참조 (apiVersion/kind/name) |
| `mission` | string | 미션 식별자 (예: `autonomous-vehicle-perception`) |
| `importance.accuracy` | float(0~1) | 정확도 가중치 |
| `importance.latency` | float(0~1) | 지연 가중치 |
| `importance.energy` | float(0~1) | 에너지 가중치 |
| `mcSpec.criticality` | string | 사용자 지정 중요도 등급 (A/C …). KETI가 A‑L‑E 패턴으로 재정의 가능 |
| `mcSpec.rtPeriod/rtWcet/rtDeadline` | int(ms) | 실시간 스케줄링 파라미터 |
| `allowPolicyOverride` | bool | true면 KETI 정책엔진이 중요도를 재정의(예: A→C) |

## 2. 직접 부착 방식 (간이) — 라벨/주석

`MaleWorkload` CR 없이 파드에 직접 A‑L‑E 점수를 부착할 수도 있다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  labels:                        # 라벨 방식
    male.keti.dev/accuracy: "0.8"
    male.keti.dev/latency: "0.9"
    male.keti.dev/energy: "0.3"
  annotations:                   # 주석 방식 (동일 키)
    male.keti.dev/accuracy: "0.8"
    male.keti.dev/latency: "0.9"
    male.keti.dev/energy: "0.3"
spec:
  containers:
    - name: app
      image: <image>
```
