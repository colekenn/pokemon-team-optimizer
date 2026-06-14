from app.engine.models import Weights
from app.engine.roles import classify
from app.engine.scoring import build_pool_vectors, evaluate
from tests.conftest import mk

W = Weights()


def test_mono_type_team_penalized_vs_diverse(tiny_pv):
    fire_team = [mk(100 + i, f"f{i}", "fire") for i in range(6)]
    diverse = [mk(200, "a", "fire"), mk(201, "b", "water"), mk(202, "c", "grass"),
               mk(203, "d", "electric"), mk(204, "e", "ground"), mk(205, "f", "steel")]
    pv = build_pool_vectors(fire_team + diverse)
    mono = evaluate(pv, list(range(6)), W)
    div = evaluate(pv, list(range(6, 12)), W)
    assert mono.shared_weakness > div.shared_weakness
    assert div.total > mono.total


def test_role_classifier_golden_cases():
    alakazam = mk(4, "alakazam", "psychic", spa=135, spe=120)
    blissey = mk(242, "blissey", "normal", hp=255, spd=135, atk=10, dfn=10)
    assert classify(alakazam) == "special sweeper"
    assert classify(blissey) == "special wall"


def test_empty_team_scores_zero(tiny_pv):
    bd = evaluate(tiny_pv, [], W)
    assert bd.total == 0.0


def test_score_components_bounded(tiny_pv):
    bd = evaluate(tiny_pv, list(range(6)), W)
    for k, v in bd.as_dict().items():
        if k != "total":
            assert 0.0 <= v <= 1.0, k


def test_weight_monotonicity(tiny_pv):
    idx = list(range(6))
    base = evaluate(tiny_pv, idx, Weights()).total
    boosted = evaluate(tiny_pv, idx, Weights(offense=5.0)).total
    assert boosted > base
