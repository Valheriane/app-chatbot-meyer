#!/usr/bin/env bash

set -e

echo "ATTENTION : cette commande supprime la base PostgreSQL Docker."
read -p "Continuer ? (y/N) " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Annulé."
  exit 0
fi

docker compose down -v
docker compose up -d --build

echo "Attente du backend..."
until curl -s http://localhost:8000/health > /dev/null; do
  sleep 3
done

docker compose exec backend python -m app.scripts.ingest_corpus

echo "Reset terminé."
echo "Streamlit : http://localhost:8501"
echo "FastAPI   : http://localhost:8000/docs"