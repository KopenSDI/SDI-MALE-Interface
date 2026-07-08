FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./

RUN python -m pip install -U pip \
&& pip install --no-cache-dir -r requirements.txt \
&& pip install --no-cache-dir "protobuf==6.31.1" "grpcio>=1.62,<2" "grpcio-tools>=1.62,<2"
COPY . .

RUN groupadd -r analysis && useradd -r -g analysis analysis \
 && chown -R analysis:analysis /app
USER analysis:analysis

# Environment variables
# (etcd related env vars removed as etcd is not used)

EXPOSE 50051
ENTRYPOINT ["python", "main.py"]
CMD ["--grpc", "--port", "50051"]
