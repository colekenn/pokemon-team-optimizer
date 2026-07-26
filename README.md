# pokemon team optimizer

A team builder for competitive Pokémon that actually optimizes instead of just showing you a type chart. You pick a format, lock in the Pokémon you definitely want (0-6 of them), and it searches for the best remaining team members and tells you why it picked each one.

Under the hood, teams are scored on offense, defense, shared weaknesses, stats, role diversity, and threat coverage, then a beam search (with greedy and random baselines for comparison) picks the best 6 out of the pool of eligible species. Built with Python/FastAPI on the backend, React + TypeScript on the frontend, Postgres for the Pokémon data, and Redis for caching. Data comes from [PokéAPI](https://pokeapi.co).

## running it

```bash
make up          # starts postgres, redis, backend, frontend (docker compose)
make ingest      # pulls ~1000 species from PokéAPI into postgres
```

Then open http://localhost:5173.

To run the backend outside docker:

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/alembic upgrade head
.venv/bin/python -m app.ingest.cli sync
.venv/bin/uvicorn app.main:app
```

## tests

```bash
make test
```

Covers the type chart against known matchups, scoring properties (mono-type teams get penalized, weights actually matter), the role classifier, beam-vs-brute-force optimality, determinism, and that locked Pokémon always stay on the team. The engine has no FastAPI or database imports so these run standalone.

## limitations / things i'd add

- No movesets, abilities, EVs, or items — it optimizes over species and typing only
- Roles are simple stat thresholds, not based on real usage
- The "threat list" is just the top 25 BST in the pool; real usage stats (e.g. Smogon) would be better
- Would be nice: side-by-side team comparison, saved teams, a genetic algorithm to compare against beam

## license

MIT
