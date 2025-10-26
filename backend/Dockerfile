# ===============================
# 🐳 Dockerfile for FastAPI app
# ===============================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install OS-level dependencies for numpy/pandas
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && apt-get clean

# Copy requirements first (for caching)
COPY backend/requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy the backend code
COPY backend .

# Expose the FastAPI port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
