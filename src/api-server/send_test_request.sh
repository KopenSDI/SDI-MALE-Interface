#!/bin/bash

# SDI Manifest Bridge API 서버로 테스트 요청을 보냅니다.
# dry_run=false 파라미터를 통해 실제 파드 생성을 요청합니다.

curl -X POST http://localhost:8000/v1/apply?dry_run=false \
-H "Content-Type: application/json" \
-d '{
  "mission": "final-test",
  "container_name": "nginx-test-pod",
  "image": "nginx:latest",
  "labels": {
    "test-label": "true"
  },
  "annotations": {
    "accuracy": "0.95",
    "latency": "0.5"
  }
}'
