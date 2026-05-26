from typing import Dict, List, Optional, Sequence

import numpy as np

from app.engine import typechart
from app.engine.models import EngineSpecies, PoolVectors, ScoreBreakdown, Weights
from app.engine.roles import DEFENSIVE_ROLES, OFFENSIVE_ROLES, ROLES, classify

# Defensive multiplier -> score contribution
_DEF_SCORE = {0.0: 1.0, 0.25: 0.75, 0.5: 0.5, 1.0: 0.25, 2.0: -0.5, 4.0: -1.0}
_SHARED_WEAK_Z = 18 * 25.0


def build_pool_vectors(
    pool: Sequence[EngineSpecies],
    threats: Optional[Sequence[EngineSpecies]] = None,
) -> PoolVectors:
    n = len(pool)
    defense = np.zeros((n, typechart.NUM_TYPES))
    coverage = np.zeros((n, typechart.NUM_TYPES), dtype=bool)
    bsts = np.array([s.bst for s in pool], dtype=np.float64)
    role_ids = np.zeros(n, dtype=np.int64)

    for i, s in enumerate(pool):
        defense[i] = typechart.defense_multipliers(s.type1, s.type2)
        coverage[i] = typechart.offensive_coverage(s.type1, s.type2)
        role_ids[i] = ROLES.index(classify(s))

    order = bsts.argsort().argsort()
    bst_percentile = order / max(n - 1, 1)

    threats = threats or []
    threat_answered = np.zeros((n, len(threats)), dtype=bool)
    for t_idx, th in enumerate(threats):
        th_def = typechart.defense_multipliers(th.type1, th.type2)
        stab_idx = [typechart.TYPE_INDEX[th.type1]]
        if th.type2:
            stab_idx.append(typechart.TYPE_INDEX[th.type2])
        for i in range(n):
            resists_stabs = all(defense[i][j] < 1.0 for j in stab_idx)
            hits_back = bool(coverage[i] @ (th_def >= 2)) or any(
                th_def[typechart.TYPE_INDEX[st]] >= 2
                for st in ([pool[i].type1] + ([pool[i].type2] if pool[i].type2 else []))
            )
            threat_answered[i, t_idx] = resists_stabs and hits_back

    return PoolVectors(
        species=list(pool),
        id_to_idx={s.id: i for i, s in enumerate(pool)},
        defense=defense,
        coverage=coverage,
        bst_percentile=bst_percentile,
        role_ids=role_ids,
        threat_answered=threat_answered,
    )


_DEF_SCORE_KEYS = np.array(sorted(_DEF_SCORE.keys()))
_DEF_SCORE_VALS = np.array([_DEF_SCORE[k] for k in sorted(_DEF_SCORE.keys())])


def _def_score(mults: np.ndarray) -> np.ndarray:
    idx = np.searchsorted(_DEF_SCORE_KEYS, np.clip(mults, 0.0, 4.0))
    return _DEF_SCORE_VALS[np.clip(idx, 0, len(_DEF_SCORE_KEYS) - 1)]


def evaluate(pv: PoolVectors, member_idx: Sequence[int], weights: Weights) -> ScoreBreakdown:
    """Score a team given pool-vector row indices (1..6 members)."""
    m = list(member_idx)
    k = len(m)
    bd = ScoreBreakdown()
    if k == 0:
        return bd

    cov = pv.coverage[m]  # (k, 18)
    bd.offense = float(cov.any(axis=0).sum()) / typechart.NUM_TYPES

    dmults = pv.defense[m]  # (k, 18)
    raw_def = _def_score(dmults).mean()  # in [-1, 1]
    bd.defense = float((raw_def + 1.0) / 2.0)

    weak_counts = (dmults >= 2.0).sum(axis=0)
    bd.shared_weakness = float(np.sum(np.maximum(0, weak_counts - 1) ** 2) / _SHARED_WEAK_Z)

    bd.stats = float(pv.bst_percentile[m].mean())

    distinct_roles = len(set(pv.role_ids[m].tolist()))
    role_names = {ROLES[r] for r in pv.role_ids[m]}
    bonus = 0.15 if (len(role_names & OFFENSIVE_ROLES) >= 1 and len(role_names & DEFENSIVE_ROLES) >= 1) else 0.0
    bd.roles = min(1.0, distinct_roles / min(6, len(ROLES)) + bonus)

    if pv.threat_answered.shape[1] > 0:
        bd.threats = float(pv.threat_answered[m].any(axis=0).mean())
    else:
        bd.threats = 0.0

    bd.total = (
        weights.offense * bd.offense
        + weights.defense * bd.defense
        - weights.shared_weakness * bd.shared_weakness
        + weights.stats * bd.stats
        + weights.roles * bd.roles
        + weights.threats * bd.threats
    )
    return bd


def weakness_matrix(pv: PoolVectors, member_idx: Sequence[int]) -> Dict[str, List[float]]:
    dmults = pv.defense[list(member_idx)]
    return {t: dmults[:, i].tolist() for i, t in enumerate(typechart.TYPES)}


def offensive_coverage_map(pv: PoolVectors, member_idx: Sequence[int]) -> Dict[str, List[str]]:
    cov = pv.coverage[list(member_idx)]
    names = [pv.species[i].name for i in member_idx]
    return {
        t: [names[j] for j in range(len(names)) if cov[j, i]]
        for i, t in enumerate(typechart.TYPES)
    }
