# Backend Dockerfile using uv
FROM python:3.12-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Define environment variable for venv location so uv finds it
ENV VIRTUAL_ENV=/opt/venv
# Add venv to path
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy dependencies
COPY pyproject.toml .
# Install dependencies into a virtual environment
RUN uv venv $VIRTUAL_ENV && \
    uv pip install -r pyproject.toml

# Final stage
FROM python:3.12-slim-bookworm

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv

# Add virtual environment to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY ./app ./app

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
