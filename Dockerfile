FROM python:3.13-slim-bookworm

RUN apt update && apt install -y --no-install-recommends curl ca-certificates pipx
ENV PATH="/root/.local/bin/:$PATH"
RUN pipx install poetry

WORKDIR /app

COPY . .

RUN poetry run sync

ENV WEB_UI_HOST=0.0.0.0
ENV WEB_UI_PORT=8888

ENV LISTEN_HOST=0.0.0.0
ENV LISTEN_PORT=3002

ENV UPSTREAM_HOST=host.docker.internal
ENV UPSTREAM_PORT=3001

ENV LOG_LEVEL=INFO

ENTRYPOINT ["poetry", "run", "mcp-sniffer"]
