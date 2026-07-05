"""Reproducible benchmark suite.

Usage: python -m benchmarks.harness [--trials 5] [--seed 42] [--out results.json]
Runs against a frozen species fixture — no DB required.
"""
import argparse
import json
import statistics
from math import comb
from pathlib import Path

from app.engine.models import EngineSpecies, Weights
from app.engine.scoring import build_pool_vectors
from app.engine.search import beam, greedy, random_baseline

FIXTURE = Path(__file__).parent / "fixtures" / "species_nondex_nolegend.json"
ALGOS = {"beam": beam.optimize, "greedy": greedy.optimize, "random": random_baseline.optimize}
POOL_SIZES = [150, 300, 500, 931]
LOCKED_COUNTS = [0, 2, 4]


def load_pool(size: int):
    rows = json.loads(FIXTURE.read_text())[:size]
    pool = [EngineSpecies(**r) for r in rows]
    threats = sorted(pool, key=lambda s: s.bst, reverse=True)[:25]
    return build_pool_vectors(pool, threats)


def run(trials: int, seed: int):
    weights = Weights()
    results = []
    for pool_size in POOL_SIZES:
        pv = load_pool(pool_size)
        if len(pv.species) < pool_size:
            continue
        for locked_n in LOCKED_COUNTS:
            locked_ids = [pv.species[i].id for i in range(locked_n)]
            k = 6 - locked_n
            space = comb(pool_size - locked_n, k)
            for algo_name, algo in ALGOS.items():
                trials_data = []
                for t in range(trials):
                    r = algo(pv, locked_ids, weights, seed=seed + t)
                    trials_data.append(r)
                scores = [r.score for r in trials_data]
                times = [r.elapsed_ms for r in trials_data]
                evals = [r.states_evaluated for r in trials_data]
                results.append({
                    "pool_size": pool_size,
                    "locked": locked_n,
                    "algorithm": algo_name,
                    "search_space": space,
                    "trials": trials,
                    "score_mean": statistics.mean(scores),
                    "score_std": statistics.pstdev(scores),
                    "elapsed_ms_mean": statistics.mean(times),
                    "elapsed_ms_std": statistics.pstdev(times),
                    "states_evaluated_mean": statistics.mean(evals),
                    "evals_per_sec": statistics.mean(evals) / (statistics.mean(times) / 1000),
                    "space_fraction": statistics.mean(evals) / space,
                })
                print(f"pool={pool_size} locked={locked_n} {algo_name:>6}: "
                      f"score={statistics.mean(scores):.3f} "
                      f"time={statistics.mean(times):.0f}ms "
                      f"evals={statistics.mean(evals):,.0f} "
                      f"({statistics.mean(evals)/(statistics.mean(times)/1000):,.0f}/s) "
                      f"space=C({pool_size - locked_n},{k})={space:.2e}")
    return results


def to_markdown(results) -> str:
    lines = [
        "| Pool | Locked | Algorithm | Search space | States evaluated | Latency (ms) | Evals/sec | Score |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['pool_size']} | {r['locked']} | {r['algorithm']} | {r['search_space']:.2e} "
            f"| {r['states_evaluated_mean']:,.0f} | {r['elapsed_ms_mean']:.0f} ± {r['elapsed_ms_std']:.0f} "
            f"| {r['evals_per_sec']:,.0f} | {r['score_mean']:.3f} ± {r['score_std']:.3f} |"
        )
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--trials", type=int, default=5)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, default=Path(__file__).parent / "results" / "latest.json")
    args = p.parse_args()

    results = run(args.trials, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2))
    md = to_markdown(results)
    args.out.with_suffix(".md").write_text(md)
    print(f"\nWrote {args.out} and {args.out.with_suffix('.md')}")


if __name__ == "__main__":
    main()
