"""add_org_id_fk

Revision ID: 65750f9f6c0b
Revises: aab74a41ee9e
Create Date: 2026-06-22 20:38:42.682275

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65750f9f6c0b'
down_revision: Union[str, None] = 'aab74a41ee9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('persons', sa.Column('org_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=True))
    op.add_column('cameras', sa.Column('org_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=True))
    op.add_column('alerts', sa.Column('org_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=True))
    op.add_column('zones', sa.Column('org_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=True))
    
    # Backfill
    op.execute("UPDATE persons SET org_id = (SELECT id FROM organizations LIMIT 1) WHERE org_id IS NULL")
    op.execute("UPDATE cameras SET org_id = (SELECT id FROM organizations LIMIT 1) WHERE org_id IS NULL")
    op.execute("UPDATE alerts SET org_id = (SELECT id FROM organizations LIMIT 1) WHERE org_id IS NULL")
    op.execute("UPDATE zones SET org_id = (SELECT id FROM organizations LIMIT 1) WHERE org_id IS NULL")

def downgrade() -> None:
    op.drop_column('zones', 'org_id')
    op.drop_column('alerts', 'org_id')
    op.drop_column('cameras', 'org_id')
    op.drop_column('persons', 'org_id')
