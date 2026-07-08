ar
ls
# 터틀봇 배터리 모니터링 시스템

터틀봇의 배터리 상태를 실시간으로 모니터링하고 관리하는 MVC 패턴 기반 웹 애플리케이션입니다.

## 🏗️ 아키텍처

### MVC 패턴 구조
```
├── app.py                 # Flask 메인 애플리케이션
├── services/
│   └── influx_service.py  # InfluxDB 서비스 레이어
├── models/
│   └── battery_model.py   # 배터리 데이터 모델
├── controllers/
│   └── battery_controller.py  # HTTP 요청 컨트롤러
└── templates/
    └── dashboard.html     # 웹 대시보드 뷰
```

## 🚀 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 애플리케이션 실행
```bash
python app.py
```

### 3. 웹 브라우저에서 접속
```
http://localhost:5000
```

## 📊 주요 기능

### 1. 실시간 배터리 모니터링
- 모든 터틀봇의 현재 배터리 상태 표시
- 배터리 잔량을 퍼센트로 변환
- 상태별 색상 구분 (High, Medium, Low, Critical)

### 2. 배터리 히스토리 차트
- 선택한 터틀봇의 24시간 배터리 사용량 그래프
- Chart.js를 사용한 인터랙티브 차트

### 3. RESTful API
- `GET /api/battery/status` - 모든 터틀봇 배터리 상태
- `GET /api/battery/<bot_name>` - 특정 터틀봇 배터리 상태
- `GET /api/bots` - 사용 가능한 터틀봇 목록
- `GET /api/battery/history/<bot_name>` - 배터리 히스토리

## 🔧 설정

### InfluxDB 연결 설정
`services/influx_service.py`에서 다음 설정을 확인하세요:

```python
INFLUX_URL = "http://<influxdb-host>:32086"
INFLUX_TOKEN = "your-token-here"
INFLUX_ORG = "keti"
INFLUX_BUCKET = "turtlebot"
```

### 터틀봇 목록
`services/influx_service.py`에서 터틀봇 목록을 수정할 수 있습니다:

```python
BOTS = ["TURTLEBOT3-Burger-1", "TURTLEBOT3-Burger-2"]
```

## 📈 배터리 상태 레벨

- **High** (>400Wh): 🟢 정상
- **Medium** (300-400Wh): 🟡 주의
- **Low** (200-300Wh): 🟠 경고
- **Critical** (<200Wh): 🔴 위험

## 🛠️ 개발

### 테스트 데이터 생성
기존 `test-input-data.py`를 사용하여 테스트 데이터를 생성할 수 있습니다:

```bash
python test-input-data.py
```

### API 테스트
```bash
# 모든 터틀봇 상태 조회
curl http://localhost:5000/api/battery/status

# 특정 터틀봇 상태 조회
curl http://localhost:5000/api/battery/TURTLEBOT3-Burger-1

# 터틀봇 목록 조회
curl http://localhost:5000/api/bots
```

## 🔄 자동 새로고침

웹 대시보드는 30초마다 자동으로 데이터를 새로고침합니다. 수동 새로고침도 가능합니다.

## 📝 로그

애플리케이션은 INFO 레벨 로그를 출력합니다. 디버그 모드에서는 더 자세한 로그를 확인할 수 있습니다. 