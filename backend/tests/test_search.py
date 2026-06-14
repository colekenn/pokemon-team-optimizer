from itertools import combinations

from app.engine.models import Weights
from app.engine.scoring import evaluate
from app.engine.search import beam, greedy, random_baseline
from app.engine.search.base import TEAM_SIZE

W = Weights()


def brute_force_best(pv, locked_ids, k):
    locked = [pv.id_to_idx[i] for i in locked_ids]
    cands = [i for i in range(len(pv.species)) if pv.species[i].id not in set(locked_ids)]
    best, best_s = None, float("-inf")
    for combo in combinations(cands, k):
        team = locked + list(combo)
        s = evaluate(pv, team, W).total
        if s > best_s:
            best, best_s = team, s
    return frozenset(best), best_s


def test_beam_finds_brute_force_optimum(tiny_pv):
    # N=12, full team of 6: C(12,6)=924 — brute-forceable
    expected, expected_score = brute_force_best(tiny_pv, [], TEAM_SIZE)
    result = beam.optimize(tiny_pv, [], W, beam_width=50)
    assert abs(result.score - expected_score) < 1e-9


def test_locked_always_present(tiny_pv):
    for algo in (beam.optimize, greedy.optimize, random_baseline.optimize):
        result = algo(tiny_pv, [4, 11], W)
        assert 4 in result.team_ids and 11 in result.team_ids
        assert len(result.team_ids) == TEAM_SIZE
        assert len(set(result.team_ids)) == TEAM_SIZE


def test_deterministic(tiny_pv):
    r1 = random_baseline.optimize(tiny_pv, [], W, seed=7, samples=500)
    r2 = random_baseline.optimize(tiny_pv, [], W, seed=7, samples=500)
    assert r1.team_ids == r2.team_ids
    b1 = beam.optimize(tiny_pv, [], W)
    b2 = beam.optimize(tiny_pv, [], W)
    assert b1.team_ids == b2.team_ids


def test_beam_geq_greedy(tiny_pv):
    b = beam.optimize(tiny_pv, [], W)
    g = greedy.optimize(tiny_pv, [], W)
    assert b.score >= g.score - 1e-9


def test_fully_locked_team(tiny_pv):
    ids = [1, 2, 3, 4, 5, 6]
    result = beam.optimize(tiny_pv, ids, W)
    assert set(result.team_ids) == set(ids)
