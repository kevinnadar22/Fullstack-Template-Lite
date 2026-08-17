# =========================
# Builder
# =========================
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Create the virtual environment and install production dependencies
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN uv sync --frozen --no-dev


# =========================
# Runtime
# =========================
FROM python:3.13-slim AS runtime

WORKDIR /app

# Runtime environment
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy only the installed environment
COPY --from=builder /app/.venv /app/.venv

# Copy application
COPY . .

# Create log directory
RUN mkdir -p /app/log

EXPOSE 8000

CMD ["uvicorn", "app.__main__:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
