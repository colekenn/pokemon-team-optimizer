"""PokéAPI → Postgres ingestion.

Usage: python -m app.ingest.cli sync [--max-gen 9] [--cache-dir .pokeapi_cache]
"""
import argparse
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db.models import Format, FormatSpecies, IngestRun, Species
from app.db.session import SessionLocal
from app.ingest.pokeapi_client import PokeApiClient

GEN_ROMAN = {
    "generation-i": 1, "generation-ii": 2, "generation-iii": 3,
    "generation-iv": 4, "generation-v": 5, "generation-vi": 6,
    "generation-vii": 7, "generation-viii": 8, "generation-ix": 9,
}
STAT_MAP = {
    "hp": "hp", "attack": "attack", "defense": "defense",
    "special-attack": "sp_attack", "special-defense": "sp_defense", "speed": "speed",
}


def transform(species_json: dict, pokemon_json: dict) -> dict:
    stats = {STAT_MAP[s["stat"]["name"]]: s["base_stat"] for s in pokemon_json["stats"]}
    types = sorted(pokemon_json["types"], key=lambda t: t["slot"])
    sprite = (
        pokemon_json["sprites"].get("other", {}).get("official-artwork", {}).get("front_default")
        or pokemon_json["sprites"].get("front_default")
    )
    return {
        "id": species_json["id"],
        "name": species_json["name"],
        "generation": GEN_ROMAN[species_json["generation"]["name"]],
        **stats,
        "bst": sum(stats.values()),
        "sprite_url": sprite,
        "is_legendary": species_json["is_legendary"],
        "is_mythical": species_json["is_mythical"],
        "type1": types[0]["type"]["name"],
        "type2": types[1]["type"]["name"] if len(types) > 1 else None,
    }


async def fetch_all(max_gen: int, cache_dir: Path) -> list:
    client = PokeApiClient(cache_dir=cache_dir)
    try:
        listing = await client.get_json("/pokemon-species?limit=2000")
        ids = [int(r["url"].rstrip("/").split("/")[-1]) for r in listing["results"]]

        async def fetch_one(sid: int):
            sp = await client.get_json(f"/pokemon-species/{sid}")
            if GEN_ROMAN[sp["generation"]["name"]] > max_gen:
                return None
            default = next((v for v in sp["varieties"] if v["is_default"]), None)
            if not default:
                return None
            pk = await client.get_json(default["pokemon"]["url"])
            return transform(sp, pk)

        rows = await asyncio.gather(*[fetch_one(i) for i in ids])
        return [r for r in rows if r]
    finally:
        await client.close()


def seed_formats(db) -> None:
    formats = [
        ("Gen 1 Classic", "Generation 1 species only", lambda s: s.generation == 1),
        ("National Dex (No Legendaries)", "All generations, legendaries/mythicals excluded",
         lambda s: not s.is_legendary and not s.is_mythical),
        ("National Dex (All)", "Every species", lambda s: True),
    ]
    all_species = db.query(Species).all()
    for name, desc, pred in formats:
        fmt = db.query(Format).filter_by(name=name).first()
        if not fmt:
            fmt = Format(name=name, description=desc)
            db.add(fmt)
            db.flush()
        existing = {fs.species_id for fs in db.query(FormatSpecies).filter_by(format_id=fmt.id)}
        for s in all_species:
            if pred(s) and s.id not in existing:
                db.add(FormatSpecies(format_id=fmt.id, species_id=s.id))
    db.commit()


def sync(max_gen: int, cache_dir: Path) -> None:
    rows = asyncio.run(fetch_all(max_gen, cache_dir))
    db = SessionLocal()
    run = IngestRun(started_at=datetime.now(timezone.utc))
    db.add(run)
    db.commit()
    try:
        for row in rows:
            stmt = pg_insert(Species).values(**row)
            stmt = stmt.on_conflict_do_update(index_elements=["id"], set_=row)
            db.execute(stmt)
        db.commit()
        seed_formats(db)
        run.species_count = len(rows)
        run.status = "success"
    except Exception:
        run.status = "failed"
        raise
    finally:
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
        db.close()
    print(f"Ingested {len(rows)} species (max gen {max_gen})")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("sync")
    p.add_argument("--max-gen", type=int, default=9)
    p.add_argument("--cache-dir", type=Path, default=Path(".pokeapi_cache"))
    args = parser.parse_args()
    if args.command == "sync":
        sync(args.max_gen, args.cache_dir)


if __name__ == "__main__":
    main()
