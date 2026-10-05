"""Rollen: is_active für users/companies, users.role wieder 16 Zeichen

Revision ID: b7c1e2f3a4d5
Revises: 1fac8aaa8fbb
Create Date: 2026-10-05 12:00:00.000000

a37133a5538b hat users.role auf 8 Zeichen gekürzt – 'superadmin' hat 10.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7c1e2f3a4d5'
down_revision: Union[str, None] = '1fac8aaa8fbb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columns(table: str) -> set[str]:
    return {c["name"] for c in sa.inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('users', 'role',
                    existing_type=sa.String(length=8),
                    type_=sa.String(length=16),
                    existing_nullable=True)
    # create_all() beim Start kann die Spalten schon angelegt haben
    if 'is_active' not in _columns('users'):
        op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
    if 'is_active' not in _columns('companies'):
        op.add_column('companies', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('companies', 'is_active')
    op.drop_column('users', 'is_active')
