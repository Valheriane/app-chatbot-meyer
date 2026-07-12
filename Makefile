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