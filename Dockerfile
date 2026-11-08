FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

COPY backend ./backend
COPY frontend ./frontend

CMD ["uv", "run", "--no-sync", "fastapi", "run", "backend/main.py", "--host", "0.0.0.0", "--port", "8000"]
