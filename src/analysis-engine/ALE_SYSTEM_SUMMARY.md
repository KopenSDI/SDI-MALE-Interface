# ALE 시스템 완전 정리 보고서

## 📋 개념 정리

### 🎯 핵심 개념
- **ALE 점수**: 실제 디바이스의 Accuracy, Latency, Energy 성능 점수 (각각 0-100점)
- **ALE 가중치**: 점수 계산 시 사용하는 비율 (각각 0-1, 합계=1)

### 🔄 함수 역할
- **GetALEWeight()**: 디바이스별 **ALE 점수**를 반환 (이름과 달리 점수 반환)
- **SetALEWeight()**: ALE **가중치** 설정
- **CalculateWeightedScore()**: 가중치를 적용한 최종 점수 계산

## 🏗️ 시스템 구조

### ALEWeightManager 클래스 (독립 클래스)
```python
class ALEWeightManager:
    # 가중치 관리
    def get_weight(device_id: str) -> Dict[str, Any]
    def set_weight(device_id: str, accuracy_weight: float, latency_weight: float, energy_weight: float, description: str) -> Dict[str, Any]
    def get_all_weights() -> Dict[str, Any]
    
    # ALE 점수 계산
    def calculate_ale_scores_for_device(device_id: str, device_data: Dict) -> Dict[str, Any]
    def calculate_ale_scores_for_devices(device_ids: list, devices_data: Dict) -> Dict[str, Any]
    
    # 가중치 적용 점수 계산
    def calculate_weighted_score(device_id: str, accuracy_value: float, latency_value: float, energy_value: float) -> Dict[str, Any]
```

### MVC 패턴 적용
- **Model (Analysis_Model)**: ALEWeightManager 위임 호출
- **Controller (Analysis_Controller)**: 비즈니스 로직 + 디바이스 데이터 수집
- **View (Analysis_View)**: gRPC 인터페이스

## 📊 데이터 구조

### ALE 점수 (ALEScore)
```json
{
  "device_id": "TURTLEBOT3-Burger-1",
  "accuracy_score": 87.5,    // 0-100점
  "latency_score": 75.2,     // 0-100점 (높을수록 좋음)
  "energy_score": 82.1,      // 0-100점 (높은 효율성)
  "calculation_timestamp": "2024-01-20T15:30:00"
}
```

### ALE 가중치 (ALEWeight)
```json
{
  "device_id": "TURTLEBOT3-Burger-1",
  "accuracy_weight": 0.4,    // 40%
  "latency_weight": 0.3,     // 30%
  "energy_weight": 0.3,      // 30%
  "description": "Burger-1 최적화 가중치",
  "last_updated": "2024-01-20T15:30:00"
}
```

## 🔧 gRPC 서비스

### GetALEWeight (실제로는 ALE 점수 반환)
```protobuf
message GetALEWeightRequest {
    string device_id = 1;  // 단일 디바이스
    repeated string device_ids = 2;  // 다중 디바이스
}

message GetALEWeightResponse {
    bool success = 1;
    string message = 2;
    int32 total_devices = 3;
    repeated ALEScore ale_scores = 4;  // ALE 점수들
    repeated string failed_devices = 5;
}
```

### SetALEWeight (가중치 설정)
```protobuf
message SetALEWeightRequest {
    string device_id = 1;
    double accuracy_weight = 2;
    double latency_weight = 3;
    double energy_weight = 4;
    string description = 5;
}
```

### CalculateWeightedScore (가중치 적용 점수)
```protobuf
message CalculateWeightedScoreRequest {
    string device_id = 1;
    double accuracy_value = 2;  // 0-1000 범위
    double latency_value = 3;   // 0-1000 범위
    double energy_value = 4;    // 0-1000 범위
    string time_range = 5;
}
```

## 🎯 사용 시나리오

### 1. 디바이스 ALE 점수 조회
```python
# 단일 디바이스 ALE 점수
result = controller.get_ale_scores_for_device("TURTLEBOT3-Burger-1")
# 결과: accuracy_score: 87.5, latency_score: 75.2, energy_score: 82.1

# 모든 디바이스 ALE 점수
result = controller.get_ale_scores_for_devices([])
# 결과: 모든 등록된 디바이스의 ALE 점수 목록
```

### 2. 디바이스별 가중치 설정
```python
# 디바이스별 가중치 설정 (정확도 중심)
controller.set_ale_weight("TURTLEBOT3-Burger-1", 0.6, 0.2, 0.2, "정확도 중심 설정")

# 디바이스별 가중치 설정 (지연시간 중심)
controller.set_ale_weight("TURTLEBOT3-Waffle-1", 0.3, 0.5, 0.2, "지연시간 중심 설정")
```

### 3. 가중치 적용 최종 점수 계산
```python
# 실제 측정값에 가중치 적용
result = controller.calculate_weighted_score(
    device_id="TURTLEBOT3-Burger-1",
    accuracy_value=850,   # 0-1000 범위 (85.0점으로 변환)
    latency_value=200,    # 0-1000 범위 (80.0점으로 변환, 낮을수록 좋음)
    energy_value=700      # 0-1000 범위 (70.0점으로 변환)
)
# 결과: weighted_score: 78.5, score_grade: "B+"
```

## 📁 파일 구조

```
Analysis/
├── ALE_Weight_Manager.py     # 독립 ALE 관리 클래스
├── Analysis_Model.py         # ALEWeightManager 위임 호출
├── Analysis_Controller.py    # 비즈니스 로직 + 디바이스 데이터 관리
└── Analysis_View.py          # gRPC 서비스 (GetALEWeight, SetALEWeight, CalculateWeightedScore)

analysis_service.proto        # protobuf 정의 (ALEScore, ALEWeight 메시지)
test_ale_weight.py           # 통합 테스트
```

## ✅ 완료된 기능

### 1. 깔끔한 분리
- ✅ ALEWeightManager: 순수 ALE 로직만 담당
- ✅ MVC 패턴: 각 레이어에서 단순 호출만 수행
- ✅ 코드 중복 제거 및 가독성 향상

### 2. 다중 디바이스 지원
- ✅ 단일 디바이스 ALE 점수 조회
- ✅ 다중 디바이스 ALE 점수 조회
- ✅ 등록된 모든 디바이스 자동 조회

### 3. 실제 디바이스 데이터 반영
- ✅ 배터리 레벨에 따른 점수 변동
- ✅ 디바이스 상태(online/busy/idle)에 따른 지연시간 점수
- ✅ 배터리 용량에 따른 에너지 효율성 점수

### 4. 가중치 관리
- ✅ 디바이스별 개별 가중치 설정
- ✅ 기본 가중치 자동 적용
- ✅ 가중치 유효성 검사 및 정규화

## 🚀 사용법

### gRPC 클라이언트에서 사용
```python
# 모든 디바이스 ALE 점수 조회
request = GetALEWeightRequest(device_id="")
response = stub.GetALEWeight(request)
# 응답: 모든 디바이스의 ALE 점수 목록

# 특정 디바이스 ALE 점수 조회
request = GetALEWeightRequest(device_id="TURTLEBOT3-Burger-1")
response = stub.GetALEWeight(request)
# 응답: 해당 디바이스의 ALE 점수

# 가중치 설정
request = SetALEWeightRequest(
    device_id="TURTLEBOT3-Burger-1",
    accuracy_weight=0.5,
    latency_weight=0.3,
    energy_weight=0.2,
    description="정확도 중심 설정"
)
response = stub.SetALEWeight(request)
```

## 📝 중요 사항

1. **GetALEWeight**: 이름과 달리 **ALE 점수**를 반환합니다
2. **다중 디바이스**: etcd 스타일로 여러 디바이스 정보를 한번에 처리
3. **MVC 분리**: 각 계층에서는 ALEWeightManager만 호출
4. **실시간 계산**: 디바이스 상태를 실시간 반영하여 ALE 점수 계산
5. **protobuf 업데이트**: ALEScore 메시지 추가로 다중 디바이스 응답 지원

---

**작성일**: 2024년 1월 20일  
**작성자**: 기철  
**버전**: v3.0 (ALE 점수 시스템 완성)

