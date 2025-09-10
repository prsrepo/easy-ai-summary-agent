FROM python:3.11.1-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y make \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock Makefile .python-version ./

RUN uv sync --frozen --no-cache

COPY ./react_hitl_agent /app/react_hitl_agent

ENV PYTHONPATH="/app/:$PYTHONPATH"

EXPOSE 8000

CMD ["make", "prod"]
