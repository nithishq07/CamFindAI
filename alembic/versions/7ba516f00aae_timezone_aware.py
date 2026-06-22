"""timezone_aware

Revision ID: 7ba516f00aae
Revises: 65750f9f6c0b
Create Date: 2026-06-22 20:41:28.337411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ba516f00aae'
down_revision: Union[str, None] = '65750f9f6c0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('cameras', 'last_seen', type_=sa.DateTime(timezone=True), postgresql_using="last_seen AT TIME ZONE 'UTC'")
    op.alter_column('persons', 'first_seen', type_=sa.DateTime(timezone=True), postgresql_using="first_seen AT TIME ZONE 'UTC'")
    op.alter_column('persons', 'last_seen', type_=sa.DateTime(timezone=True), postgresql_using="last_seen AT TIME ZONE 'UTC'")
    op.alter_column('tracks', 'start_ts', type_=sa.DateTime(timezone=True), postgresql_using="start_ts AT TIME ZONE 'UTC'")
    op.alter_column('tracks', 'end_ts', type_=sa.DateTime(timezone=True), postgresql_using="end_ts AT TIME ZONE 'UTC'")
    op.alter_column('trajectory_points', 'frame_ts', type_=sa.DateTime(timezone=True), postgresql_using="frame_ts AT TIME ZONE 'UTC'")
    op.alter_column('alerts', 'frame_ts', type_=sa.DateTime(timezone=True), postgresql_using="frame_ts AT TIME ZONE 'UTC'")
    op.alter_column('alerts', 'acknowledged_at', type_=sa.DateTime(timezone=True), postgresql_using="acknowledged_at AT TIME ZONE 'UTC'")
    op.alter_column('alerts', 'resolved_at', type_=sa.DateTime(timezone=True), postgresql_using="resolved_at AT TIME ZONE 'UTC'")
    op.alter_column('camera_health_log', 'timestamp', type_=sa.DateTime(timezone=True), postgresql_using="timestamp AT TIME ZONE 'UTC'")

def downgrade() -> None:
    pass
    pass
