# Kinyu High-Performance Justfile
# Tools:
# - python: uv
# - frontend: pnpm

# Default target
default: install build

# --- Installation ---

# Install all dependencies
install: install-tools install-backend install-frontend

# Install system tools (uv, pnpm)
install-tools:
    @echo "Checking system dependencies..."
    # Check/Install uv
    @if ! command -v uv >/dev/null 2>&1; then \
        echo "uv not found. Installing uv..."; \
        curl -LsSf https://astral.sh/uv/install.sh | sh; \
        echo "Please restart your shell or run 'source $HOME/.cargo/env' (if using cargo) or add ~/.local/bin to PATH"; \
    else \
        echo "uv is already installed."; \
    fi
    # Check/Install pnpm
    @if ! command -v pnpm >/dev/null 2>&1; then \
        echo "pnpm not found. Installing pnpm..."; \
        if command -v npm >/dev/null 2>&1; then \
            sudo npm install -g pnpm; \
        else \
            echo "Node.js/npm not found. Using standalone script..."; \
            curl -fsSL https://get.pnpm.io/install.sh | sh -; \
        fi \
    else \
        echo "pnpm is already installed."; \
    fi

# Install backend dependencies
install-backend:
    @echo "Installing backend with uv..."
    # Ensure uv is in path for this shell execution if just installed
    @export PATH="$HOME/.local/bin:$PATH" && \
    cd backend && uv venv && uv pip install -r pyproject.toml

# Install frontend dependencies
install-frontend:
    @echo "Installing frontend with pnpm..."
    # Ensure pnpm is in path for this shell execution if just installed
    @export PATH="$HOME/.local/share/pnpm:$PATH" && \
    cd frontend && pnpm install

# --- Testing ---

# Run backend tests
# Note: Just always runs from the project root, so 'cd backend' works from any subdirectory
test:
    @echo "Running backend tests..."
    @export PATH="$HOME/.local/bin:$PATH" && \
    cd backend && \
    uv pip install pytest pytest-asyncio && \
    .venv/bin/pytest

# --- Local Development ---

# Start local development environment
dev:
    @echo "Starting local development environment..."
    docker compose up --build

# Stop local development environment
stop:
    docker compose down

# --- Building for Production ---

# Build production Docker images
build:
    @echo "Building production Docker images..."
    docker compose build

# --- Deployment (Docker Swarm) ---

# Deploy to Docker Swarm stack 'kinyu'
# Ensure you have initialized swarm: docker swarm init
deploy:
    @echo "Deploying to Docker Swarm stack 'kinyu'..."
    docker stack deploy -c docker-compose.yml kinyu

# --- Utilities ---

# Clean artifacts
clean:
    @echo "Cleaning artifacts..."
    rm -rf backend/.venv
    rm -rf frontend/node_modules
    rm -rf frontend/.output
    rm -rf frontend/.nuxt

# Generate backend OpenAPI schema
swagger:
    @echo "Generating OpenAPI schema..."
    # This assumes you have the venv activated or use run
    cd backend && ../backend/.venv/bin/python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > openapi.json
