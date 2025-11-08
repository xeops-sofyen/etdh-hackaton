# Dockerfile for Heimdall Olympe Development
#
# This allows testing the Olympe SDK on non-Linux systems
# Build: docker build -t heimdall .
# Run: docker run -it -p 8000:8000 heimdall

FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --upgrade pip

# Set working directory
WORKDIR /app

# Copy backend code (includes requirements.txt)
COPY backend/ /app/backend/
COPY playbooks/ /app/playbooks/
COPY tests/ /app/tests/

# Install Python dependencies
# Note: parrot-olympe is optional (not available on PyPI, must be installed separately)
# The code handles missing Olympe gracefully - install all other dependencies
RUN grep -v "^parrot-olympe" backend/requirements.txt | grep -v "^#" | grep -v "^$" > /tmp/requirements.txt && \
    pip3 install -r /tmp/requirements.txt && \
    echo "Note: parrot-olympe skipped (optional, not on PyPI)"

# Set PYTHONPATH so Python can find the backend module
ENV PYTHONPATH=/app

# Expose API port
EXPOSE 8000

# Default command
CMD ["python3", "backend/api/main.py"]
