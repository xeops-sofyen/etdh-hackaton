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
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --upgrade pip

# Set working directory
WORKDIR /app

# Copy backend code
COPY backend/ /app/backend/
COPY playbooks/ /app/playbooks/
COPY tests/ /app/tests/

# Install Python dependencies
RUN pip3 install parrot-olympe pydantic fastapi uvicorn pytest python-dotenv

# Expose API port
EXPOSE 8000

# Default command
CMD ["python3", "backend/api/main.py"]
