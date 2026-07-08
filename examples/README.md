# 예시 모음

두 가지 형태의 예시를 제공한다.

## 1. `requests/*.json` — API Server로 보내는 요청 (ETRI가 보내는 형태)

ETRI가 API Server(`sdi_manifest_bridge`)로 POST하는 JSON이다. API Server가 이 입력을 받아 K8s 매니페스트로 보강·적용한다.

| 파일 | 미션 | A / L / E |
| --- | --- | --- |
| `requests/autonomous-driving.json` | 자율주행 | 0.6 / 0.3 / 0.1 |
| `requests/object-detection.json` | 객체탐지 | 0.3 / 0.5 / 0.2 |
| `requests/navigation.json` | 내비게이션 | 0.4 / 0.5 / 0.1 |

### 입력 필드 (전체)
| 필드 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `mission` | ✅ | | 미션 식별자 |
| `container_name` | ✅ | | 컨테이너 이름 |
| `image` | ✅ | | 컨테이너 이미지 |
| `accuracy` / `latency` / `energy` | | 0.5 / 0.3 / 0.2 | A‑L‑E 값 (각 0~1) |
| `criticality` | | `A` | 중요도 등급 (A/B/C) |
| `rt_period` / `rt_wcet` / `rt_deadline` | | 100 / 30 / 100 | 실시간 파라미터 (ms) |
| `namespace` | | `sdi-demo` | 배포 네임스페이스 |
| `labels` / `annotations` | | | 추가 라벨/주석 (Deployment에 병합) |

### 생성 결과 (JSON 1건 → 리소스 3종)
API Server는 이 입력으로 다음을 함께 생성한다.
1. **Deployment** — 워크로드 (`{mission}-{container_name}`)
2. **MaleWorkload** (`male.keti.dev/v1alpha1`) — 위 Deployment에 A‑L‑E·중요도 주입
3. **PropagationPolicy** (Karmada) — `intent-driven` 배치 + `schedulerName: sdi-scheduler`

### 보내는 방법
```bash
# 미리보기 (변환된 YAML만 확인, 적용 안 함)
curl -X POST "http://<api-server-host>:8000/v1/render" \
  -H "Content-Type: application/json" \
  -d @requests/object-detection.json

# 실제 적용 (dry_run=false)
curl -X POST "http://<api-server-host>:8000/v1/apply?dry_run=false" \
  -H "Content-Type: application/json" \
  -d @requests/object-detection.json
```

## 2. `*.yaml` — MaleWorkload CR (선언 형태)

같은 미션을 CR로 직접 선언한 예시다. Deployment + MaleWorkload 형태이며, GitOps나 `kubectl apply`로 클러스터에 적용한다.

- `autonomous-driving.yaml` / `object-detection.yaml` / `navigation.yaml`

## 두 형태의 관계
- **JSON 요청**: API Server를 통해 워크로드를 생성 (간이 입력 → 보강)
- **MaleWorkload CR**: 기존 워크로드에 MALE 요구사항을 CR로 부착

둘 다 최종적으로 A‑L‑E 값이 오케스트레이션에 반영되는 것은 동일하다.
