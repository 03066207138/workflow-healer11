# Use compatible Python version
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && apt-get clean

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --upgrade pip setuptools wheel numpy Cython meson ninja
RUN pip install -r requirements.txt

COPY backend .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
