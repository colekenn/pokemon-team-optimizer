.PHONY: up down ingest test bench

up:
	docker compose up -d --build

down:
	docker compose down

ingest:
	docker compose exec backend python -m app.ingest.cli sync

test:
	cd backend && .venv/bin/python -m pytest -q

bench:
	cd backend && .venv/bin/python -m benchmarks.harness --trials 5
