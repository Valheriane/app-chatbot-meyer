start:
	./scripts/start_app.sh

stop:
	./scripts/stop_app.sh

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

ingest:
	docker compose exec backend python -m app.scripts.ingest_corpus

reset:
	./scripts/reset_app.sh

	build:
	docker compose build

rebuild:
	docker compose down
	docker compose up -d --build --force-recreate

rebuild-backend:
	docker compose up -d --build --force-recreate backend

rebuild-frontend:
	docker compose up -d --build --force-recreate frontend

rebuild-no-cache:
	docker compose down
	docker compose build --no-cache
	docker compose up -d --force-recreate

restart:
	docker compose restart

ps:
	docker compose ps