#!/bin/bash
echo "Starting CamFindAI Backend Services..."

# Ensure we're in the right directory and environment is set up

echo "Waiting for PostgreSQL..."
until nc -z "${POSTGRES_HOST:-localhost}" 5432; do
  sleep 2
done
echo "PostgreSQL is ready."

echo "Running Alembic migrations..."
alembic upgrade head

echo "Waiting for Kafka..."
until nc -z localhost 29092; do
  sleep 3
done
echo "Kafka is ready."
# 1. Start FastAPI in background
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# 2. Start Matching Engine Consumer
python app/consumers/matching_consumer.py &
MATCH_PID=$!

# 3. Start Persistence Consumer
python app/consumers/persistence_consumer.py &
PERSIST_PID=$!

# 4. Start Rules Engine Consumer
python app/consumers/rules_engine.py &
RULES_PID=$!

# 5. Start Multi-Camera Worker Manager
python app/workers/multi_camera_worker.py &
WORKER_PID=$!

echo "====================================="
echo "All core services started successfully."
echo "API is running at http://localhost:8000"
echo "====================================="
echo "Note: The Multi-Camera Worker Manager is running in the background."
echo "You can add and start cameras from the UI Dashboard."
echo ""
echo "Press CTRL+C to stop all services."

# Catch Ctrl+C to kill all background processes
trap "kill $API_PID $MATCH_PID $PERSIST_PID $RULES_PID $WORKER_PID; exit" INT TERM EXIT

# Wait for all processes
wait
