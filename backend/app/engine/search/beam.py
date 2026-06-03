import time
from typing import List, Sequence, Set, Tuple

from app.engine.models import OptimizationResult, PoolVectors, Weights
from app.engine.search.base import (
    TEAM_SIZE, Evaluator, candidate_indices, locked_indices, make_result,
)

DEFAULT_BEAM_WIDTH = 200
POLISH_TOP = 5


def _local_search(
    ev: Evaluator, team: List[int], candidates: List[int], swappable: Set[int]
) -> Tuple[List[int], float]:
    """Steepest-ascent single-swap hill climbing on unlocked slots."""
    best = list(team)
    best_score = ev.score(best)
    improved = True
    while improved:
        improved = False
        member_set = set(best)
        for slot in range(len(best)):
            if best[slot] not in swappable:
                continue
            for c in candidates:
                if c in member_set:
                    continue
                trial = list(best)
                trial[slot] = c
                s = ev.score(trial)
                if s > best_score:
                    best, best_score = trial, s
                    member_set = set(best)
                    improved = True
    return best, best_score


def optimize(
    pv: PoolVectors,
    locked_ids: Sequence[int],
    weights: Weights,
    seed: int = 0,
    excluded_ids: Sequence[int] = (),
    beam_width: int = DEFAULT_BEAM_WIDTH,
) -> OptimizationResult:
    """Beam search over partial teams + single-swap hill-climb polish.

    Candidates are only appended in ascending index order (canonical
    ordering), so each combination is generated exactly once.
    """
    started = time.perf_counter()
    ev = Evaluator(pv, weights)
    locked = locked_indices(pv, locked_ids)
    candidates = candidate_indices(pv, locked_ids, excluded_ids)
    k = TEAM_SIZE - len(locked)

    if k == 0:
        return make_result("beam", ev, locked, started)

    # beam entries: (score, team, last_added_idx)
    beam: List[Tuple[float, List[int], int]] = [(ev.score(locked) if locked else 0.0, locked, -1)]
    for _ in range(k):
        expansions: List[Tuple[float, List[int], int]] = []
        for _, team, last in beam:
            for c in candidates:
                if c <= last:
                    continue
                new_team = team + [c]
                expansions.append((ev.score(new_team), new_team, c))
        expansions.sort(key=lambda e: e[0], reverse=True)
        beam = expansions[:beam_width]

    swappable = set(candidates)
    best_team, best_score = beam[0][1], beam[0][0]
    for _, team, _ in beam[:POLISH_TOP]:
        polished, s = _local_search(ev, team, candidates, swappable)
        if s > best_score:
            best_team, best_score = polished, s

    return make_result("beam", ev, best_team, started)
