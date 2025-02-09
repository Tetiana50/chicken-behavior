# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopencv-dev \
    python3-opencv \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p storage/videos storage/frames

# Expose ports
EXPOSE 8000 8501

# Create entrypoint script
RUN echo '#!/bin/bash\n\
if [ "$1" = "api" ]; then\n\
    uvicorn app.main:app --host 0.0.0.0 --port 8000\n\
elif [ "$1" = "frontend" ]; then\n\
    streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0\n\
else\n\
    echo "Please specify either 'api' or 'frontend' as the first argument"\n\
    exit 1\n\
fi' > /entrypoint.sh && chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"] 