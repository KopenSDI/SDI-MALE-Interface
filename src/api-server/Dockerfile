# Stage 1: Builder stage
FROM python:3.11-slim as builder

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Add user's local python packages to path
ENV PATH=/root/.local/bin:$PATH

# Copy the application code
COPY ./sdi_manifest_bridge /app/sdi_manifest_bridge

EXPOSE 8000

# Run the application
CMD ["uvicorn", "sdi_manifest_bridge.main:app", "--host", "0.0.0.0", "--port", "8000"]
