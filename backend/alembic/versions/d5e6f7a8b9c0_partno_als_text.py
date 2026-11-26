"""Sachnummer (partno) als Text speichern

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-11-26 12:00:00.000000

Sachnummern enthalten oft Buchstaben, Leerzeichen oder Bindestriche
(z. B. "A 123 456-01"). Bisher war die Spalte eine Zahl. Vorhandene
Zahlen bleiben beim Umwandeln erhalten.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5e6f7a8b9c0'
down_revision: Union[str, None] = 'c4d5e6f7a8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'ana_mu', 'partno',
        existing_type=sa.Integer(),
        type_=sa.String(length=64),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'ana_mu', 'partno',
        existing_type=sa.String(length=64),
        type_=sa.Integer(),
        existing_nullable=True,
    )
