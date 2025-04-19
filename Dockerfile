FROM python:3.13-slim-bookworm

RUN apt update && apt install -y --no-install-recommends curl ca-certificates
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

COPY frontend/dist /app/frontend/dist

COPY backend /app/backend

RUN cd backend && uv sync

ENV WEB_UI_PORT=8888
ENV LISTEN_PORT=3002
ENV LISTEN_HOST=0.0.0.0
ENV UPSTREAM_HOST=host.docker.internal
ENV UPSTREAM_PORT=3001

ENTRYPOINT ["uv", "--directory", "/app/backend", "run", "python", "src/main.py"]
