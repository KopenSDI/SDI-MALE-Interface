# KETI Analysis Engine - gRPC 서버

Analysis Engine을 gRPC 서버로 실행하여 분석 결과를 클라이언트에게 제공하는 시스템입니다.

## 주요 기능

- **디바이스 관리**: 터틀봇 생성, 상태 조회, 목록 관리
- **InfluxDB 연동**: 실시간 배터리 데이터 업데이트
- **성능 분석**: 디바이스별 성능 점수, 효율성, 배터리 건강도 분석
- **플릿 분석**: 전체 디바이스 플릿의 통계 및 분석
- **비상 정지**: 긴급 상황 시 디바이스 제어
- **gRPC API**: 다양한 클라이언트에서 호출 가능한 API

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. gRPC 서버 실행

```bash
# 기본 포트(50051)로 gRPC 서버 시작
python main.py --grpc

# 커스텀 포트로 실행
python main.py --grpc --port 8080

# 엔진 이름 지정
python main.py --grpc --name "MyAnalysisEngine" --port 50051
```

### 3. 서버 상태 확인

서버가 시작되면 다음과 같은 메시지가 출력됩니다:
```
Engine Name: KETI-AnalysisEngine
gRPC 서버 모드로 실행 (포트: 50051)
gRPC 분석 서버가 포트 50051에서 시작되었습니다.
분석 엔진과 gRPC 서버가 동시에 실행됩니다.
Ctrl+C로 서버를 중지할 수 있습니다.
```

## gRPC API 서비스

### 1. CreateTurtlebot
터틀봇 디바이스를 생성하고 시스템에 등록합니다.

**요청:**
```protobuf
CreateTurtlebotRequest {
    string device_id = 1;
    string model = 2;
    string location = 3;
}
```

**응답:**
```protobuf
CreateTurtlebotResponse {
    bool success = 1;
    string message = 2;
    DeviceInfo device_info = 3;
}
```

### 2. GetDeviceStatus
특정 디바이스의 현재 상태를 조회합니다.

**요청:**
```protobuf
GetDeviceStatusRequest {
    string device_id = 1;
}
```

### 3. UpdateFromInflux
InfluxDB에서 최신 배터리 데이터를 가져와 디바이스 상태를 업데이트합니다.

**요청:**
```protobuf
UpdateFromInfluxRequest {
    string device_id = 1;
    string lookback = 2;  // 예: "-30m"
}
```

### 4. AnalyzeDevice
디바이스의 성능을 분석하여 점수와 메트릭을 제공합니다.

**응답에 포함되는 분석 데이터:**
- 성능 점수 (0-100)
- 효율성 등급
- 배터리 건강도
- 분석 요약
- 세부 메트릭들

### 5. GetFleetAnalysis
전체 디바이스 플릿의 통합 분석 결과를 제공합니다.

### 6. GetAllDevices
시스템에 등록된 모든 디바이스 목록을 조회합니다.

### 7. GetBatteryStatus
특정 디바이스의 상세 배터리 정보를 조회합니다.

### 8. EmergencyStop
디바이스의 비상 정지를 활성화/해제합니다.

## 클라이언트 테스트

### 테스트 클라이언트 실행

```bash
python grpc_client_test.py
```

이 명령으로 모든 gRPC API를 자동으로 테스트할 수 있습니다.

### 수동 테스트 예제

Python에서 직접 클라이언트 호출:

```python
import grpc
import analysis_service_pb2 as pb2
import analysis_service_pb2_grpc as pb2_grpc

# 서버 연결
channel = grpc.insecure_channel('localhost:50051')
stub = pb2_grpc.AnalysisServiceStub(channel)

# 터틀봇 생성
request = pb2.CreateTurtlebotRequest(
    device_id="my-turtlebot",
    model="TURTLEBOT3-Burger", 
    location="Office"
)
response = stub.CreateTurtlebot(request)
print(f"결과: {response.success}, 메시지: {response.message}")

# 디바이스 분석
request = pb2.AnalyzeDeviceRequest(device_id="my-turtlebot")
response = stub.AnalyzeDevice(request)
if response.success:
    print(f"성능 점수: {response.analysis.performance_score}")
    print(f"배터리 건강도: {response.analysis.battery_health}")
```

## 실제 데이터 연동

### InfluxDB 데이터 사용

실제 터틀봇의 InfluxDB 데이터를 사용하려면:

1. InfluxDB 설정이 올바른지 확인 (`AnalysisEngine.py`의 INFLUX_* 변수들)
2. 실제 터틀봇 이름으로 업데이트 호출:

```python
# 실제 터틀봇 데이터 업데이트
request = pb2.UpdateFromInfluxRequest(
    device_id="TURTLEBOT3-Burger-1",  # 실제 터틀봇 ID
    lookback="-1h"  # 1시간 전부터 데이터 조회
)
response = stub.UpdateFromInflux(request)
```

## 아키텍처

```
┌─────────────────┐    gRPC     ┌──────────────────┐
│   gRPC Client   │◄──────────► │  Analysis_View   │
│                 │             │  (gRPC Server)   │
└─────────────────┘             └──────────────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │ Analysis_        │
                                │ Controller       │
                                └──────────────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │ Analysis_Model   │
                                │                  │
                                │ ┌──────────────┐ │
                                │ │ InfluxReader │ │
                                │ └──────────────┘ │
                                └──────────────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │    InfluxDB      │
                                │  (Turtlebot Data)│
                                └──────────────────┘
```

## 문제 해결

### 서버가 시작되지 않는 경우

1. 포트가 이미 사용 중인지 확인:
```bash
netstat -tulpn | grep :50051
```

2. 다른 포트로 실행:
```bash
python main.py --grpc --port 8080
```

### InfluxDB 연결 오류

1. InfluxDB 서버가 실행 중인지 확인
2. `AnalysisEngine.py`의 InfluxDB 설정 확인
3. 네트워크 연결 및 토큰 권한 확인

### gRPC 의존성 오류

```bash
pip install grpcio grpcio-tools protobuf
```

## 개발자 정보

이 시스템은 기존의 MVC 패턴 분석 엔진을 확장하여 gRPC 서버 기능을 추가한 것입니다.

- **View**: gRPC 서버 역할 (Analysis_View.py)
- **Controller**: 비즈니스 로직 처리 (Analysis_Controller.py)  
- **Model**: 데이터 관리 및 InfluxDB 연동 (Analysis_Model.py)

분석 결과는 단순한 SDI 정보가 아닌 실제 성능 분석, 배터리 건강도, 효율성 등급 등의 가치있는 분석 데이터를 제공합니다.