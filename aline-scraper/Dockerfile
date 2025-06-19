# Multi-stage build for optimization
FROM python:3.9-slim as base
# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Application setup
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 