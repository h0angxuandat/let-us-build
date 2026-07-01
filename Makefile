# let-us-build — dev tasks
.PHONY: install sync up down api web cli lint type test check

install sync:            ## install/refresh the uv workspace
	uv sync

up:                      ## start backing services (Postgres+pgvector)
	docker compose up -d

down:                    ## stop backing services
	docker compose down

api:                     ## run the core API (dev)
	uv run uvicorn lub_api.main:create_app --factory --reload --port 8300

cli:                     ## run the CLI (pass ARGS="...")
	uv run let-us-build $(ARGS)

lint:                    ## ruff lint
	uv run ruff check .

type:                    ## mypy
	uv run mypy packages apps

test:                    ## pytest
	uv run pytest -q

check: lint type test    ## lint + type + test
