FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    postgresql-client \
    redis-tools \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Install Docker CLI
RUN curl -fsSL https://get.docker.com | sh

# Create non-root user with sudo access
RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid vscode --shell /bin/bash --create-home vscode \
    && usermod -aG docker vscode \
    && echo 'vscode ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Set working directory
WORKDIR /workspace

# Switch to non-root user
USER vscode

# Set environment variables
ENV PYTHONPATH="/workspace"
ENV PATH="/workspace/.venv/bin:$PATH"
