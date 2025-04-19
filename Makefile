IMAGE_NAME = mcp-sniffer
WEB_UI_PORT ?= 8888
LISTEN_PORT ?= 3002
LISTEN_HOST ?= 0.0.0.0
UPSTREAM_HOST ?= host.docker.internal
UPSTREAM_PORT ?= 3001

build:
	cd frontend && npm run build
	docker build -t $(IMAGE_NAME) .

run:
	docker run -it \
		-p $(WEB_UI_PORT):$(WEB_UI_PORT) \
		-p $(LISTEN_PORT):$(LISTEN_PORT) \
		--network bridge \
		-e WEB_UI_PORT=$(WEB_UI_PORT) \
		-e LISTEN_PORT=$(LISTEN_PORT) \
		-e LISTEN_HOST=$(LISTEN_HOST) \
		-e UPSTREAM_HOST=$(UPSTREAM_HOST) \
		-e UPSTREAM_PORT=$(UPSTREAM_PORT) \
		$(IMAGE_NAME)
