import time
from typing import Dict, FrozenSet, List, Sequence, Tuple

from app.engine.models import OptimizationResult, PoolVectors, ScoreBreakdown, Weights
from app.engine.scoring import evaluate

TEAM_SIZE = 6


class Evaluator:
    """Memoizing team evaluator; counts states evaluated."""

    def __init__(self, pv: PoolVectors, weights: Weights):
        self.pv = pv
        self.weights = weights
        self._memo: Dict[FrozenSet[int], float] = {}
        self.evaluations = 0

    def score(self, member_idx: Sequence[int]) -> float:
        key = frozenset(member_idx)
        cached = self._memo.get(key)
        if cached is not None:
            return cached
        self.evaluations += 1
        s = evaluate(self.pv, member_idx, self.weights).total
        self._memo[key] = s
        return s

    def breakdown(self, member_idx: Sequence[int]) -> ScoreBreakdown:
        return evaluate(self.pv, member_idx, self.weights)


def make_result(
    algorithm: str,
    ev: Evaluator,
    team: Sequence[int],
    started: float,
) -> OptimizationResult:
    bd = ev.breakdown(team)
    ids = tuple(ev.pv.species[i].id for i in team)
    return OptimizationResult(
        team_ids=ids,
        score=bd.total,
        breakdown=bd,
        states_evaluated=ev.evaluations,
        elapsed_ms=(time.perf_counter() - started) * 1000,
        algorithm=algorithm,
    )


def locked_indices(pv: PoolVectors, locked_ids: Sequence[int]) -> List[int]:
    return [pv.id_to_idx[i] for i in locked_ids]


def candidate_indices(pv: PoolVectors, locked_ids: Sequence[int], excluded_ids: Sequence[int]) -> List[int]:
    banned = set(locked_ids) | set(excluded_ids)
    return [i for i, s in enumerate(pv.species) if s.id not in banned]
