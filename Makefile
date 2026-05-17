.PHONY: dev dev-build stop migrate seed test lint

dev:
	docker compose -f infra/docker-compose.yml up

dev-build:
	docker compose -f infra/docker-compose.yml up --build

stop:
	docker compose -f infra/docker-compose.yml down

migrate:
	docker compose -f infra/docker-compose.yml exec api alembic upgrade head

seed:
	docker compose -f infra/docker-compose.yml exec api python -m data.ingest

test:
	docker compose -f infra/docker-compose.test.yml up -d
	docker compose -f infra/docker-compose.test.yml exec postgres_test sh -c 'until pg_isready -U history; do sleep 1; done'
	cd apps/api && DATABASE_URL=postgresql+asyncpg://history:history@localhost:5433/history_test REDIS_URL=redis://localhost:6380 pytest tests/ -v; EXIT_CODE=$$?; docker compose -f infra/docker-compose.test.yml down; exit $$EXIT_CODE

lint:
	cd apps/api && ruff check app/ tests/
