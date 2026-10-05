"""add fk_company to all tables

Revision ID: 4affad0bccfa
Revises: 0c96451899d5
Create Date: 2026-08-26 16:02:01.679309

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4affad0bccfa'
down_revision: Union[str, None] = '0c96451899d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('modells', sa.Column('fk_company', sa.Integer(), sa.ForeignKey('companies.id'), nullable=True))
    op.add_column('mod_components', sa.Column('fk_company', sa.Integer(), sa.ForeignKey('companies.id'), nullable=True))
    op.add_column('ana_mu', sa.Column('fk_company', sa.Integer(), sa.ForeignKey('companies.id'), nullable=True))
    op.add_column('anakomp', sa.Column('fk_company', sa.Integer(), sa.ForeignKey('companies.id'), nullable=True))
    op.add_column('anakonst', sa.Column('fk_company', sa.Integer(), sa.ForeignKey('companies.id'), nullable=True))
    op.add_column('kmgs', sa.Column('fk_company', sa.Integer(), sa.ForeignKey('companies.id'), nullable=True))

def downgrade() -> None:
    op.drop_column('modells', 'fk_company')
    op.drop_column('mod_components', 'fk_company')
    op.drop_column('ana_mu', 'fk_company')
    op.drop_column('anakomp', 'fk_company')
    op.drop_column('anakonst', 'fk_company')
    op.drop_column('kmgs', 'fk_company')