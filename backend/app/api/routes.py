from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api import schemas
from app.cache import redis_cache
from app.db.models import Format, FormatSpecies, Species
from app.db.session import get_db
from app.engine.models import Weights
from app.engine.explain import explain_member
from app.engine.roles import ROLES
from app.engine.scoring import evaluate, offensive_coverage_map, weakness_matrix
from app.engine.search import beam, greedy, random_baseline
from app.services import optimizer_service as svc

router = APIRouter(prefix="/api/v1")

ALGORITHMS = {"beam": beam.optimize, "greedy": greedy.optimize, "random": random_baseline.optimize}


@router.get("/healthz")
def healthz():
    return {"status": "ok"}


@router.get("/formats", response_model=List[schemas.FormatOut])
def list_formats(db: Session = Depends(get_db)):
    rows = (
        db.query(Format, func.count(FormatSpecies.id))
        .outerjoin(FormatSpecies)
        .group_by(Format.id)
        .order_by(Format.id)
        .all()
    )
    return [
        schemas.FormatOut(id=f.id, name=f.name, description=f.description, pool_size=n)
        for f, n in rows
    ]


@router.get("/pokemon", response_model=List[schemas.SpeciesOut])
def list_pokemon(format_id: int, search: Optional[str] = None, db: Session = Depends(get_db)):
    pv = svc.load_pool(db, format_id)
    out = [svc.species_out(s) for s in pv.species]
    if search:
        q = search.lower()
        out = [s for s in out if q in s["name"]]
    return out


def _validate_members(pv, ids: List[int]):
    missing = [i for i in ids if i not in pv.id_to_idx]
    if missing:
        raise HTTPException(422, f"Species not in format pool: {missing}")
    if len(set(ids)) != len(ids):
        raise HTTPException(422, "Duplicate species in team")


@router.post("/analyze", response_model=schemas.AnalyzeResponse)
def analyze(req: schemas.AnalyzeRequest, db: Session = Depends(get_db)):
    key = redis_cache.cache_key("analysis", req.model_dump())
    cached = redis_cache.get_json(key)
    if cached:
        cached["cache_hit"] = True
        return cached

    pv = svc.load_pool(db, req.format_id)
    _validate_members(pv, req.species_ids)
    idx = [pv.id_to_idx[i] for i in req.species_ids]
    weights = svc.weights_from(req.weights)
    bd = evaluate(pv, idx, weights)
    resp = schemas.AnalyzeResponse(
        score=bd.total,
        breakdown=bd.as_dict(),
        weakness_matrix=weakness_matrix(pv, idx),
        member_ids=req.species_ids,
        offensive_coverage=offensive_coverage_map(pv, idx),
        roles={pv.species[i].name: ROLES[pv.role_ids[i]] for i in idx},
    ).model_dump()
    redis_cache.set_json(key, resp)
    return resp


@router.post("/optimize", response_model=schemas.OptimizeResponse)
def optimize(req: schemas.OptimizeRequest, db: Session = Depends(get_db)):
    if req.algorithm not in ALGORITHMS:
        raise HTTPException(422, f"Unknown algorithm: {req.algorithm}")
    key = redis_cache.cache_key("opt", req.model_dump())
    cached = redis_cache.get_json(key)
    if cached:
        cached["cache_hit"] = True
        return cached

    pv = svc.load_pool(db, req.format_id)
    _validate_members(pv, req.locked_ids)
    weights = svc.weights_from(req.weights)

    before_score = None
    if req.locked_ids:
        before_score = evaluate(pv, [pv.id_to_idx[i] for i in req.locked_ids], weights).total

    result = ALGORITHMS[req.algorithm](
        pv, req.locked_ids, weights, seed=req.seed, excluded_ids=req.excluded_ids
    )

    team_idx = [pv.id_to_idx[i] for i in result.team_ids]
    locked_set = set(req.locked_ids)
    recommendations = []
    for i, sid in zip(team_idx, result.team_ids):
        if sid in locked_set:
            continue
        reasons, marginals = explain_member(pv, team_idx, i, weights)
        recommendations.append(schemas.Recommendation(
            species=svc.species_out(pv.species[i]),
            reasons=reasons,
            marginal_contribution=marginals,
        ))

    resp = schemas.OptimizeResponse(
        team=[svc.species_out(pv.species[i]) for i in team_idx],
        score=result.score,
        breakdown=result.breakdown.as_dict(),
        before_score=before_score,
        recommendations=recommendations,
        states_evaluated=result.states_evaluated,
        elapsed_ms=result.elapsed_ms,
    ).model_dump()
    redis_cache.set_json(key, resp)
    return resp
