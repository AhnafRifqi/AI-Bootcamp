# Dockerfile untuk IT Helpdesk Agent API
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dan install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code dan data
COPY app/ ./app/
COPY data/ ./data/

# Expose port FastAPI
EXPOSE 8000

# Jalankan aplikasi dengan uvicorn (API key dikirim via environment variable saat docker run)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]