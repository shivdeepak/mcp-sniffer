FROM node:22.15-bookworm-slim

WORKDIR /app/frontend

COPY frontend/package.json .

WORKDIR /app/frontend

RUN npm install

COPY frontend .

COPY .devcontainer/react-container/start.sh /app/start.sh

CMD ["/app/start.sh"]
