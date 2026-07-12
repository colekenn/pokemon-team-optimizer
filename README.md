# pokemon team optimizer

A team builder for competitive Pokémon that actually optimizes instead of just showing you a type chart. You pick a format, lock in the Pokémon you definitely want (0-6 of them), and it searches for the best remaining team members and tells you why it picked each one.

Built with Python/FastAPI on the backend, React + TypeScript on the frontend, Postgres for the Pokémon data, and Redis for caching. Data comes from [PokéAPI](https://pokeapi.co).

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

## how the optimizer works

A team is scored on six things, each normalized to 0-1 and weighted (weights are adjustable in the UI request):

- **offense** - how many of the 18 types the team hits super-effectively with STAB
- **defense** - how well the team takes hits of each type (immunities good, 4x weaknesses bad)
- **shared weaknesses** - quadratic penalty when multiple members are weak to the same type
- **stats** - average base stat total percentile within the pool
- **role diversity** - roles like sweeper/wall/tank derived from base stats
- **threat coverage** - can someone on the team switch into and beat each of the format's top threats

The problem is picking the best 6 from up to 931 species — C(931,6) is about 8.9×10^14 teams, so you can't check them all. I implemented three search strategies behind one interface so they could be compared fairly:

- `beam` - beam search that builds the team slot by slot keeping the best 200 partial teams, then polishes the top results with single-swap hill climbing
- `greedy` - just picks the best marginal addition each slot (baseline)
- `random` - 10,000 random teams, keep the best (baseline)

There's a test that brute-forces a small pool (C(12,6) = 924 teams) and checks that beam search finds the exact optimum.

Scoring is fast because everything about a species is precomputed into numpy vectors when the pool loads, so evaluating a team is just a few array operations. Search-internal memoization is a plain dict — I originally considered Redis for it, but a Redis round trip is way slower than the evaluation itself. Redis instead caches whole API responses, so re-running the same optimization returns instantly.

## benchmarks

`make bench` runs every combination of pool size × locked count × algorithm against a frozen species snapshot (no DB needed), 3+ trials each, seeded. Results from my machine:

| pool | locked | algorithm | search space | evaluated | latency | score |
|---|---|---|---|---|---|---|
| 931 | 0 | beam | 8.9e14 | 159,987 | 4.45s | 3.868 |
| 931 | 0 | greedy | 8.9e14 | 5,571 | 0.15s | 3.779 |
| 931 | 0 | random | 8.9e14 | 10,000 | 0.32s | 3.329 |
| 500 | 0 | beam | 2.1e13 | 139,920 | 3.84s | 3.801 |
| 150 | 0 | beam | 1.4e10 | 33,674 | 0.91s | 3.605 |

Beam beats random by about 16% and greedy by 2-4%. Honestly greedy is closer than I expected — the objective seems fairly smooth. Throughput is around 35k team evaluations/sec in a single process. With 4 Pokémon locked the remaining space is tiny and all three algorithms find the same answer.

Full table gets written to `backend/benchmarks/results/latest.md`.

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
