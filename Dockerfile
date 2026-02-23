# Morse Code Trainer - Docker Image
# 
# Build: docker build -t morse-trainer .
# Run tests: docker run --rm morse-trainer pytest
# Run app (requires X11): docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix morse-trainer

FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SDL_AUDIODRIVER=dummy
ENV SDL_VIDEODRIVER=dummy

# Install system dependencies for pygame and Tkinter
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-dev \
    libsdl2-mixer-dev \
    libsdl2-image-dev \
    libsdl2-ttf-dev \
    python3-tk \
    tk-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY . .

# Set working directory for tests
WORKDIR /app/src

# Default command runs tests
CMD ["pytest", "--tb=short", "-v"]
