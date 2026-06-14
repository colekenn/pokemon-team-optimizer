from typing import List

import pytest

from app.engine.models import EngineSpecies
from app.engine.scoring import build_pool_vectors


def mk(id, name, t1, t2=None, hp=80, atk=80, dfn=80, spa=80, spd=80, spe=80):
    return EngineSpecies(
        id=id, name=name, type1=t1, type2=t2, hp=hp, attack=atk, defense=dfn,
        sp_attack=spa, sp_defense=spd, speed=spe,
        bst=hp + atk + dfn + spa + spd + spe,
    )


@pytest.fixture
def tiny_pool() -> List[EngineSpecies]:
    return [
        mk(1, "charizard", "fire", "flying", atk=84, spa=109, spe=100),
        mk(2, "blastoise", "water", dfn=100, spd=105),
        mk(3, "venusaur", "grass", "poison", spa=100, spd=100),
        mk(4, "alakazam", "psychic", spa=135, spe=120, hp=55, dfn=45),
        mk(5, "machamp", "fighting", atk=130, hp=90),
        mk(6, "golem", "rock", "ground", dfn=130, atk=120, spe=45),
        mk(7, "gengar", "ghost", "poison", spa=130, spe=110, hp=60),
        mk(8, "dragonite", "dragon", "flying", atk=134, hp=91),
        mk(9, "jolteon", "electric", spa=110, spe=130, hp=65),
        mk(10, "lapras", "water", "ice", hp=130, spd=95),
        mk(11, "snorlax", "normal", hp=160, atk=110, spd=110, spe=30),
        mk(12, "scizor", "bug", "steel", atk=130, dfn=100),
    ]


@pytest.fixture
def tiny_pv(tiny_pool):
    return build_pool_vectors(tiny_pool)
