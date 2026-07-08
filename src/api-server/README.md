# SDI Manifest Bridge

SDI Manifest Bridge는 단순화된 명세(Manifest)를 입력받아 쿠버네티스 환경에 적합한 전체 명세로 변환하고, 이를 클러스터에 배포하는 역할을 하는 API 서버입니다.

주로 Ansible과 같은 외부 도구로부터 간단한 요청을 받아, 내부적으로 사전에 정의된 템플릿과 결합하여 완전한 쿠버네티스 파드(Pod) 명세를 생성합니다. 이 과정에서 SDI(Software Defined Infrastructure) 환경에 필요한 특정 레이블(Label)과 어노테이션(Annotation)을 자동으로 추가하여, 전체 인프라와의 유기적인 연동을 지원합니다.

## 주요 기능

- **단순 명세 변환**: `mission`, `container_name`, `image` 등 최소한의 정보만으로 쿠버네티스 파드 명세를 생성합니다.
- **자동 인리치먼트(Enrichment)**: SDI에서 사용하는 `accuracy`, `latency`, `energy`와 같은 커스텀 어노테이션을 자동으로 추가합니다.
- **쿠버네티스 배포**: REST API 엔드포인트 (`/v1/apply`)를 통해 생성된 명세를 쿠버네티스 클러스터에 직접 배포(Server-Side Apply)합니다.
- **템플릿 기반 관리**: 파드 템플릿을 컨피그맵(ConfigMap)으로 관리하여, 배포 환경에 따라 유연하게 설정을 변경할 수 있습니다.

## 프로젝트 구조

```
.
├── kubernetes_manifests/ # 쿠버네티스 배포를 위한 명세 파일
│   ├── 00-namespace.yaml
│   ├── 01-rbac.yaml
│   ├── 02-configmap.yaml
│   ├── 03-deployment.yaml
│   └── 04-service.yaml
├── sdi_manifest_bridge/  # FastAPI 애플리케이션 소스 코드
│   ├── core/             # 명세 변환 및 강화 로직
│   ├── k8s/              # 쿠버네티스 클라이언트
│   └── main.py           # API 엔드포인트 정의
├── tests/                # 테스트 코드
├── Dockerfile            # 컨테이너 이미지 빌드를 위한 Dockerfile
├── requirements.txt      # Python 의존성 목록
└── README.md             # 프로젝트 설명 파일
```

## 배포 방법

이 애플리케이션은 쿠버네티스 클러스터에 배포하는 것을 전제로 합니다. 아래의 `deploy.sh` 스크립트를 사용하여 관련 리소스를 한 번에 배포할 수 있습니다.

**요구사항**:
- `kubectl`이 설치되고, 타겟 클러스터에 대한 접근 권한이 설정되어 있어야 합니다.

**배포 명령어**:
```bash
# 스크립트에 실행 권한을 부여합니다.
chmod +x deploy.sh

# 스크립트를 실행하여 sdi-manifest-bridge 네임스페이스에 리소스를 배포합니다.
./deploy.sh
```

스크립트는 `kubernetes_manifests` 디렉토리의 YAML 파일들을 순서대로 적용하여, 독립된 `sdi-manifest-bridge` 네임스페이스에 모든 리소스를 생성합니다.
