from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


@dataclass(frozen=True)
class EngineSpecies:
    id: int
    name: str
    type1: str
    type2: Optional[str]
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int
    bst: int
    sprite_url: Optional[str] = None
    generation: int = 1


@dataclass(frozen=True)
class Weights:
    offense: float = 1.0
    defense: float = 1.0
    shared_weakness: float = 0.8
    stats: float = 0.6
    roles: float = 0.5
    threats: float = 1.2


@dataclass
class PoolVectors:
    """Precomputed per-species vectors for fast team evaluation."""
    species: List[EngineSpecies]
    id_to_idx: Dict[int, int]
    defense: np.ndarray        # (N, 18) defensive multipliers
    coverage: np.ndarray       # (N, 18) bool STAB super-effective coverage
    bst_percentile: np.ndarray  # (N,)
    role_ids: np.ndarray       # (N,) int
    threat_answered: np.ndarray  # (N, T) bool — member answers threat t


@dataclass
class ScoreBreakdown:
    offense: float = 0.0
    defense: float = 0.0
    shared_weakness: float = 0.0
    stats: float = 0.0
    roles: float = 0.0
    threats: float = 0.0
    total: float = 0.0

    def as_dict(self) -> Dict[str, float]:
        return {
            "offense": self.offense, "defense": self.defense,
            "shared_weakness": self.shared_weakness, "stats": self.stats,
            "roles": self.roles, "threats": self.threats, "total": self.total,
        }


@dataclass
class OptimizationResult:
    team_ids: Tuple[int, ...]
    score: float
    breakdown: ScoreBreakdown
    states_evaluated: int
    elapsed_ms: float
    algorithm: str = ""
    per_member_marginals: Dict[int, Dict[str, float]] = field(default_factory=dict)
