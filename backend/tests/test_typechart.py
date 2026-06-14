import numpy as np

from app.engine import typechart as tc


def eff(atk, dfn):
    return tc.CHART[tc.TYPE_INDEX[atk], tc.TYPE_INDEX[dfn]]


def test_known_matchups():
    assert eff("ground", "electric") == 2
    assert eff("normal", "ghost") == 0
    assert eff("electric", "ground") == 0
    assert eff("water", "fire") == 2
    assert eff("fire", "water") == 0.5
    assert eff("dragon", "fairy") == 0
    assert eff("fighting", "normal") == 2
    assert eff("poison", "steel") == 0
    assert eff("ghost", "normal") == 0


def test_dual_type_defense_stacks():
    # ground vs fire/flying (charizard): 2 * 0 = 0
    v = tc.defense_multipliers("fire", "flying")
    assert v[tc.TYPE_INDEX["ground"]] == 0
    # rock vs fire/flying: 2 * 2 = 4
    assert v[tc.TYPE_INDEX["rock"]] == 4


def test_chart_shape_and_values():
    assert tc.CHART.shape == (18, 18)
    assert set(np.unique(tc.CHART)) <= {0.0, 0.5, 1.0, 2.0}
