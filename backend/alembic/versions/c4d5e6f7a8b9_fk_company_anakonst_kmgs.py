"""fk_company für anakonst und kmgs sicherstellen

Revision ID: c4d5e6f7a8b9
Revises: b7c1e2f3a4d5
Create Date: 2026-10-06 12:00:00.000000

Der doppelte Migrationszweig (4affad0bccfa & Vorgänger) wurde entfernt.
Er hat als einziger fk_company in anakonst und kmgs angelegt – das holt
diese Migration nach. Bestehende Datenbanken, die die Spalten schon haben,
bleiben unverändert.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4d5e6f7a8b9'
down_revision: Union[str, None] = 'b7c1e2f3a4d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = ('anakonst', 'kmgs')


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in sa.inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    """Upgrade schema."""
    for table in TABLES:
        if not _has_column(table, 'fk_company'):
            op.add_column(table, sa.Column('fk_company', sa.Integer(), nullable=True))
            op.create_foreign_key(f'fk_{table}_fk_company', table, 'companies', ['fk_company'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # bewusst leer: die Spalten können aus dem alten Zweig stammen
    pass
