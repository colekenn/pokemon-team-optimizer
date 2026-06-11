from typing import Dict, List, Sequence, Tuple

from app.engine import typechart
from app.engine.models import PoolVectors, Weights
from app.engine.roles import ROLES
from app.engine.scoring import evaluate


def explain_member(
    pv: PoolVectors,
    team_idx: Sequence[int],
    member: int,
    weights: Weights,
) -> Tuple[List[str], Dict[str, float]]:
    """Reasons + marginal component contribution of one member (team without vs with)."""
    without = [i for i in team_idx if i != member]
    bd_with = evaluate(pv, team_idx, weights)
    bd_without = evaluate(pv, without, weights)
    marginals = {
        k: round(bd_with.as_dict()[k] - bd_without.as_dict()[k], 4)
        for k in ("offense", "defense", "shared_weakness", "stats", "roles", "threats", "total")
    }

    reasons: List[str] = []
    sp = pv.species[member]

    cov_without = pv.coverage[without].any(axis=0) if without else pv.coverage[[]].any(axis=0)
    new_cov = [typechart.TYPES[t] for t in range(typechart.NUM_TYPES)
               if pv.coverage[member][t] and not cov_without[t]]
    if new_cov:
        reasons.append(f"Adds super-effective coverage vs {', '.join(t.title() for t in new_cov)}")

    if without:
        resists = pv.defense[member] < 1.0
        weak_counts = (pv.defense[without] >= 2.0).sum(axis=0)
        patched = [typechart.TYPES[t] for t in range(typechart.NUM_TYPES)
                   if weak_counts[t] >= 2 and resists[t]]
        if patched:
            reasons.append(f"Resists {', '.join(t.title() for t in patched)}, a weakness shared by teammates")

    immune = [typechart.TYPES[t] for t in range(typechart.NUM_TYPES) if pv.defense[member][t] == 0.0]
    if immune:
        reasons.append(f"Immune to {', '.join(t.title() for t in immune)}")

    role = ROLES[pv.role_ids[member]]
    other_roles = {ROLES[pv.role_ids[i]] for i in without}
    if role not in other_roles:
        reasons.append(f"Only {role} on the team")

    if pv.bst_percentile[member] >= 0.8:
        reasons.append(f"Top-tier base stats (BST {sp.bst}, {int(pv.bst_percentile[member] * 100)}th percentile in pool)")

    if pv.threat_answered.shape[1] > 0 and without:
        answered_without = pv.threat_answered[without].any(axis=0)
        newly = int((pv.threat_answered[member] & ~answered_without).sum())
        if newly:
            reasons.append(f"Answers {newly} otherwise-uncovered top threat{'s' if newly > 1 else ''}")

    if not reasons:
        reasons.append("Best remaining net contribution to overall team score")
    return reasons, marginals
