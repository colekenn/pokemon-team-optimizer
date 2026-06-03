import time
from typing import Sequence

from app.engine.models import OptimizationResult, PoolVectors, Weights
from app.engine.search.base import (
    TEAM_SIZE, Evaluator, candidate_indices, locked_indices, make_result,
)


def optimize(
    pv: PoolVectors,
    locked_ids: Sequence[int],
    weights: Weights,
    seed: int = 0,
    excluded_ids: Sequence[int] = (),
) -> OptimizationResult:
    """Greedy marginal-gain fill baseline."""
    started = time.perf_counter()
    ev = Evaluator(pv, weights)
    team = locked_indices(pv, locked_ids)
    candidates = set(candidate_indices(pv, locked_ids, excluded_ids))

    while len(team) < TEAM_SIZE and candidates:
        best_c, best_s = None, float("-inf")
        for c in candidates:
            s = ev.score(team + [c])
            if s > best_s:
                best_c, best_s = c, s
        team.append(best_c)
        candidates.discard(best_c)

    return make_result("greedy", ev, team, started)
