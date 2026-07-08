#!/bin/bash

# 이 스크립트는 SDI Manifest Bridge 애플리케이션을 쿠버네티스 클러스터에 배포합니다.
# 스크립트가 위치한 디렉토리 기준으로 kubernetes_manifests 경로를 사용합니다.

set -e  # 오류 발생 시 스크립트 중단

BASE_DIR=$(dirname "$0")
MANIFEST_DIR="${BASE_DIR}/kubernetes_manifests"

# 1. 네임스페이스 생성
echo "Applying 00-namespace.yaml..."
kubectl apply -f "${MANIFEST_DIR}/00-namespace.yaml"

# 2. RBAC (ServiceAccount, Role, RoleBinding) 생성
echo "Applying 01-rbac.yaml..."
kubectl apply -f "${MANIFEST_DIR}/01-rbac.yaml"

# 3. 컨피그맵 생성
echo "Applying 02-configmap.yaml..."
kubectl apply -f "${MANIFEST_DIR}/02-configmap.yaml"

# 4. 디플로이먼트 생성
echo "Applying 03-deployment.yaml..."
kubectl apply -f "${MANIFEST_DIR}/03-deployment.yaml"

# 5. 서비스 생성
echo "Applying 04-service.yaml..."
kubectl apply -f "${MANIFEST_DIR}/04-service.yaml"

echo -e "\nDeployment complete. All resources have been applied to the 'sdi-manifest-bridge' namespace."
echo "To check the status of the deployment, run: kubectl get all -n sdi-manifest-bridge"
