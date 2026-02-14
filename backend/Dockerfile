FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies (only essential ones)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Create log directory
RUN mkdir -p /app/log

# Expose port for the web service
EXPOSE 8000

# Default command (will be overridden in docker-compose)
CMD ["uv", "run", "uvicorn", "app.__main__:app", "--host", "0.0.0.0", "--port", "8000"]
