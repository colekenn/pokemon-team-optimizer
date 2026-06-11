from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SpeciesOut(BaseModel):
    id: int
    name: str
    generation: int
    types: List[str]
    stats: Dict[str, int]
    bst: int
    sprite_url: Optional[str]
    role: str


class FormatOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    pool_size: int


class WeightsIn(BaseModel):
    offense: float = 1.0
    defense: float = 1.0
    shared_weakness: float = 0.8
    stats: float = 0.6
    roles: float = 0.5
    threats: float = 1.2


class AnalyzeRequest(BaseModel):
    species_ids: List[int] = Field(max_length=6)
    format_id: int
    weights: Optional[WeightsIn] = None


class AnalyzeResponse(BaseModel):
    score: float
    breakdown: Dict[str, float]
    weakness_matrix: Dict[str, List[float]]  # attacking type -> per-member multiplier
    member_ids: List[int]
    offensive_coverage: Dict[str, List[str]]  # target type -> member names covering it
    roles: Dict[str, str]  # member name -> role
    cache_hit: bool = False


class OptimizeRequest(BaseModel):
    format_id: int
    locked_ids: List[int] = Field(default_factory=list, max_length=6)
    excluded_ids: List[int] = Field(default_factory=list)
    weights: Optional[WeightsIn] = None
    algorithm: str = "beam"  # beam | greedy | random
    seed: int = 42


class Recommendation(BaseModel):
    species: SpeciesOut
    reasons: List[str]
    marginal_contribution: Dict[str, float]


class OptimizeResponse(BaseModel):
    team: List[SpeciesOut]
    score: float
    breakdown: Dict[str, float]
    before_score: Optional[float]
    recommendations: List[Recommendation]
    states_evaluated: int
    elapsed_ms: float
    cache_hit: bool = False
