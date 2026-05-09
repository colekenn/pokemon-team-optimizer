"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-12
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "species",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(64), nullable=False, index=True),
        sa.Column("generation", sa.Integer, nullable=False),
        sa.Column("hp", sa.Integer, nullable=False),
        sa.Column("attack", sa.Integer, nullable=False),
        sa.Column("defense", sa.Integer, nullable=False),
        sa.Column("sp_attack", sa.Integer, nullable=False),
        sa.Column("sp_defense", sa.Integer, nullable=False),
        sa.Column("speed", sa.Integer, nullable=False),
        sa.Column("bst", sa.Integer, nullable=False),
        sa.Column("sprite_url", sa.String(256)),
        sa.Column("is_legendary", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("is_mythical", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("type1", sa.String(16), nullable=False),
        sa.Column("type2", sa.String(16)),
    )
    op.create_table(
        "formats",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(64), nullable=False, unique=True),
        sa.Column("description", sa.String(256)),
    )
    op.create_table(
        "format_species",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("format_id", sa.Integer, sa.ForeignKey("formats.id"), nullable=False, index=True),
        sa.Column("species_id", sa.Integer, sa.ForeignKey("species.id"), nullable=False),
        sa.UniqueConstraint("format_id", "species_id"),
    )
    op.create_table(
        "ingest_runs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("started_at", sa.DateTime, nullable=False),
        sa.Column("finished_at", sa.DateTime),
        sa.Column("species_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(16), nullable=False, server_default="running"),
    )


def downgrade() -> None:
    op.drop_table("ingest_runs")
    op.drop_table("format_species")
    op.drop_table("formats")
    op.drop_table("species")
