from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Species(Base):
    __tablename__ = "species"

    id: Mapped[int] = mapped_column(primary_key=True)  # national dex id
    name: Mapped[str] = mapped_column(String(64), index=True)
    generation: Mapped[int]
    hp: Mapped[int]
    attack: Mapped[int]
    defense: Mapped[int]
    sp_attack: Mapped[int]
    sp_defense: Mapped[int]
    speed: Mapped[int]
    bst: Mapped[int]
    sprite_url: Mapped[Optional[str]] = mapped_column(String(256))
    is_legendary: Mapped[bool] = mapped_column(default=False)
    is_mythical: Mapped[bool] = mapped_column(default=False)
    type1: Mapped[str] = mapped_column(String(16))
    type2: Mapped[Optional[str]] = mapped_column(String(16))


class Format(Base):
    __tablename__ = "formats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(256))
    entries: Mapped[List["FormatSpecies"]] = relationship(back_populates="format")


class FormatSpecies(Base):
    __tablename__ = "format_species"
    __table_args__ = (UniqueConstraint("format_id", "species_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    format_id: Mapped[int] = mapped_column(ForeignKey("formats.id"), index=True)
    species_id: Mapped[int] = mapped_column(ForeignKey("species.id"))
    format: Mapped["Format"] = relationship(back_populates="entries")


class IngestRun(Base):
    __tablename__ = "ingest_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    started_at: Mapped[datetime]
    finished_at: Mapped[Optional[datetime]]
    species_count: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(16), default="running")
