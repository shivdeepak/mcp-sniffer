lint:
	cd frontend && npm run lint
	poetry run ruff check .
	poetry run ruff format --check .

build:
	cd .devcontainer && docker compose build

start:
	cd .devcontainer && docker compose up -d

stop:
	cd .devcontainer && docker compose down

clean:
	cd .devcontainer && docker compose down
	cd .devcontainer && docker compose rm -f

prune:
	docker system prune -a -f
	docker image prune -a -f
	docker volume prune -f
	docker network prune -f

release:
	cd frontend && npm run build
	poetry build
