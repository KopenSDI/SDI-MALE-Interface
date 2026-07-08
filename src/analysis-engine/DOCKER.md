# 🐳 SDI Analysis Engine Docker 가이드

이 문서는 SDI Analysis Engine을 Docker 컨테이너로 실행하는 방법을 설명합니다.

## 📋 목차

- [빠른 시작](#빠른-시작)
- [상세 사용법](#상세-사용법)
- [Docker Compose 사용](#docker-compose-사용)
- [트러블슈팅](#트러블슈팅)

## 🚀 빠른 시작

### 1. Docker 이미지 빌드
```bash
./docker-build.sh
```

### 2. 컨테이너 실행
```bash
./docker-run.sh start
```

### 3. 상태 확인
```bash
./docker-run.sh status
```

### 4. 로그 확인
```bash
./docker-run.sh logs
```

## 📖 상세 사용법

### Docker 수동 빌드
```bash
docker build -t sdi-analysis-engine:latest .
```

### Docker 수동 실행
```bash
docker run -d \
  --name sdi-analysis-engine \
  -p 50051:50051 \
  -v "$(pwd)/influxdDB-Information.txt:/app/influxdDB-Information.txt:ro" \
  -v "$(pwd)/influxDB-TOKEN.txt:/app/influxDB-TOKEN.txt:ro" \
  sdi-analysis-engine:latest
```

### 컨테이너 관리 명령어

#### docker-run.sh 스크립트 사용
```bash
# 컨테이너 시작
./docker-run.sh start

# 컨테이너 중지
./docker-run.sh stop

# 컨테이너 재시작
./docker-run.sh restart

# 실시간 로그 확인
./docker-run.sh logs

# 컨테이너 상태 확인
./docker-run.sh status

# 이미지 빌드
./docker-run.sh build
```

#### 직접 Docker 명령어 사용
```bash
# 컨테이너 상태 확인
docker ps -a | grep sdi-analysis-engine

# 로그 확인
docker logs sdi-analysis-engine

# 컨테이너 내부 접속
docker exec -it sdi-analysis-engine /bin/bash

# 컨테이너 중지
docker stop sdi-analysis-engine

# 컨테이너 제거
docker rm sdi-analysis-engine
```

## 🐳 Docker Compose 사용

### 1. 서비스 시작
```bash
docker-compose up -d
```

### 2. 서비스 중지
```bash
docker-compose down
```

### 3. 로그 확인
```bash
docker-compose logs -f analysis-engine
```

### 4. 서비스 재시작
```bash
docker-compose restart analysis-engine
```

## 🔌 포트 및 연결

- **gRPC 포트**: `50051`
- **연결 테스트**: 
  ```bash
  # gRPC 클라이언트 테스트
  python grpc_client_test.py
  ```

## 📁 볼륨 마운트

컨테이너는 다음 파일들을 호스트에서 마운트합니다:

- `influxdDB-Information.txt`: InfluxDB 연결 정보
- `influxDB-TOKEN.txt`: InfluxDB 인증 토큰

이 파일들이 없으면 컨테이너가 제대로 작동하지 않을 수 있습니다.

## 🌐 환경 변수

컨테이너에서 사용하는 주요 환경 변수:

- `PYTHONUNBUFFERED=1`: Python 출력 버퍼링 비활성화

## 🔧 트러블슈팅

### 일반적인 문제들

#### 1. 포트 충돌
```bash
# 포트 사용 중인 프로세스 확인
sudo netstat -tlnp | grep :50051

# 다른 포트로 실행
docker run -d -p 50052:50051 --name sdi-analysis-engine sdi-analysis-engine:latest
```

#### 2. 권한 문제
```bash
# 스크립트 실행 권한 부여
chmod +x docker-build.sh docker-run.sh
```

#### 3. 이미지 빌드 실패
```bash
# Docker 캐시 무시하고 빌드
docker build --no-cache -t sdi-analysis-engine:latest .
```

#### 4. 컨테이너가 시작되지 않음
```bash
# 자세한 에러 로그 확인
docker logs sdi-analysis-engine

# 컨테이너 내부에서 디버깅
docker run -it --entrypoint /bin/bash sdi-analysis-engine:latest
```

#### 5. InfluxDB 연결 문제
- `influxdDB-Information.txt`와 `influxDB-TOKEN.txt` 파일이 존재하는지 확인
- InfluxDB 서버가 실행 중인지 확인
- 네트워크 연결 상태 확인

### 로그 레벨 조정
```bash
# 디버그 모드로 실행
docker run -d \
  --name sdi-analysis-engine \
  -p 50051:50051 \
  -e LOG_LEVEL=DEBUG \
  sdi-analysis-engine:latest
```

### 성능 모니터링
```bash
# 컨테이너 리소스 사용량 확인
docker stats sdi-analysis-engine

# 컨테이너 정보 확인
docker inspect sdi-analysis-engine
```

## 🔄 업데이트 및 유지보수

### 1. 이미지 업데이트
```bash
# 새 이미지 빌드
./docker-build.sh

# 컨테이너 재시작
./docker-run.sh restart
```

### 2. 컨테이너 정리
```bash
# 중지된 컨테이너 정리
docker container prune

# 사용하지 않는 이미지 정리
docker image prune

# 전체 시스템 정리 (주의!)
docker system prune -a
```

## 📚 추가 리소스

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [gRPC Python 가이드](https://grpc.io/docs/languages/python/)













