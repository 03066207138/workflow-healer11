# ===============================
# 🐳 Dockerfile for FastAPI app
# ===============================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install minimal system dependencies required for numpy/pandas
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    && apt-get clean

# Copy requirements first (for caching)
COPY backend/requirements.txt .

# Upgrade pip and ensure wheel builds properly
RUN pip install --upgrade pip setuptools wheel

# Use stable, precompiled pandas/numpy versions to avoid source builds
RUN sed -i 's/pandas==.*/pandas==2.1.1/' requirements.txt && \
    sed -i 's/numpy==.*/numpy==1.26.4/' requirements.txt || true

# Install dependencies
RUN pip install -r requirements.txt --no-cache-dir

# Copy backend source code
COPY backend .

# Expose FastAPI port
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
