#!/usr/bin/env bash

set -e

echo "===================================="
echo " Lancement de Meyer RAG avec Docker "
echo "===================================="

echo ""
echo "1) Construction et lancement des conteneurs..."
docker compose up -d --build

echo ""
echo "2) Attente du backend FastAPI..."

until curl -s http://localhost:8000/health > /dev/null; do
  echo "   Backend pas encore prêt..."
  sleep 3
done

echo "   Backend prêt."

echo ""
echo "3) Vérification de la base documentaire..."

STATS=$(curl -s http://localhost:8000/documents/stats || echo "")

echo "   Stats actuelles : $STATS"

if echo "$STATS" | grep -q '"chunks":0'; then
  echo ""
  echo "4) Aucun chunk trouvé. Lancement de l'ingestion..."
  docker compose exec backend python -m app.scripts.ingest_corpus
else
  echo ""
  echo "4) Des chunks semblent déjà présents. Ingestion ignorée."
  echo "   Pour forcer une nouvelle ingestion, lance :"
  echo "   docker compose exec backend python -m app.scripts.ingest_corpus"
fi

echo ""
echo "===================================="
echo " Application prête "
echo "===================================="
echo "Frontend Streamlit : http://localhost:8501"
echo "Backend FastAPI    : http://localhost:8000/docs"
echo "Healthcheck        : http://localhost:8000/health"
echo "===================================="