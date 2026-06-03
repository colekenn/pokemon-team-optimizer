import random
import time
from typing import Sequence

from app.engine.models import OptimizationResult, PoolVectors, Weights
from app.engine.search.base import (
    TEAM_SIZE, Evaluator, candidate_indices, locked_indices, make_result,
)

DEFAULT_SAMPLES = 10_000


def optimize(
    pv: PoolVectors,
    locked_ids: Sequence[int],
    weights: Weights,
    seed: int = 42,
    excluded_ids: Sequence[int] = (),
    samples: int = DEFAULT_SAMPLES,
) -> OptimizationResult:
    """Random-sampling baseline: draw N random completions, keep the best."""
    started = time.perf_counter()
    ev = Evaluator(pv, weights)
    locked = locked_indices(pv, locked_ids)
    candidates = candidate_indices(pv, locked_ids, excluded_ids)
    k = TEAM_SIZE - len(locked)
    rng = random.Random(seed)

    best_team, best_score = None, float("-inf")
    for _ in range(samples):
        team = locked + rng.sample(candidates, k)
        s = ev.score(team)
        if s > best_score:
            best_team, best_score = team, s

    return make_result("random", ev, best_team, started)
