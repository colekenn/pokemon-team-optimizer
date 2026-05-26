from typing import List

from app.engine.models import EngineSpecies

ROLES: List[str] = [
    "physical sweeper", "special sweeper", "physical wall", "special wall",
    "tank", "mixed attacker", "utility",
]
ROLE_INDEX = {r: i for i, r in enumerate(ROLES)}

OFFENSIVE_ROLES = {"physical sweeper", "special sweeper", "mixed attacker"}
DEFENSIVE_ROLES = {"physical wall", "special wall", "tank"}


def classify(s: EngineSpecies) -> str:
    if s.attack >= 100 and s.speed >= 95:
        return "physical sweeper"
    if s.sp_attack >= 100 and s.speed >= 95:
        return "special sweeper"
    if s.defense >= 100 and s.hp >= 80:
        return "physical wall"
    if s.sp_defense >= 100 and s.hp >= 80:
        return "special wall"
    if s.hp >= 85 and max(s.attack, s.sp_attack) >= 90:
        return "tank"
    if s.attack >= 90 and s.sp_attack >= 90:
        return "mixed attacker"
    return "utility"
