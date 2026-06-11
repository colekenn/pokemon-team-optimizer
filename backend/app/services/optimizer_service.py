"""Bridges DB rows → engine pool vectors, runs searches, shapes API responses."""
from typing import Dict, List, Optional, Sequence

from sqlalchemy.orm import Session

from app.db.models import FormatSpecies, Species
from app.engine.models import EngineSpecies, PoolVectors, Weights
from app.engine.roles import ROLES, classify
from app.engine.scoring import build_pool_vectors

THREAT_COUNT = 25  # top-BST pool members used as the format threat list

_pool_cache: Dict[int, PoolVectors] = {}


def to_engine_species(s: Species) -> EngineSpecies:
    return EngineSpecies(
        id=s.id, name=s.name, type1=s.type1, type2=s.type2,
        hp=s.hp, attack=s.attack, defense=s.defense,
        sp_attack=s.sp_attack, sp_defense=s.sp_defense, speed=s.speed,
        bst=s.bst, sprite_url=s.sprite_url, generation=s.generation,
    )


def load_pool(db: Session, format_id: int) -> PoolVectors:
    if format_id in _pool_cache:
        return _pool_cache[format_id]
    rows: List[Species] = (
        db.query(Species)
        .join(FormatSpecies, FormatSpecies.species_id == Species.id)
        .filter(FormatSpecies.format_id == format_id)
        .order_by(Species.id)
        .all()
    )
    pool = [to_engine_species(s) for s in rows]
    threats = sorted(pool, key=lambda s: s.bst, reverse=True)[:THREAT_COUNT]
    pv = build_pool_vectors(pool, threats)
    _pool_cache[format_id] = pv
    return pv


def clear_pool_cache() -> None:
    _pool_cache.clear()


def species_out(sp: EngineSpecies) -> dict:
    return {
        "id": sp.id,
        "name": sp.name,
        "generation": sp.generation,
        "types": [t for t in (sp.type1, sp.type2) if t],
        "stats": {
            "hp": sp.hp, "attack": sp.attack, "defense": sp.defense,
            "sp_attack": sp.sp_attack, "sp_defense": sp.sp_defense, "speed": sp.speed,
        },
        "bst": sp.bst,
        "sprite_url": sp.sprite_url,
        "role": classify(sp),
    }


def weights_from(payload) -> Weights:
    if payload is None:
        return Weights()
    return Weights(**payload.model_dump())
