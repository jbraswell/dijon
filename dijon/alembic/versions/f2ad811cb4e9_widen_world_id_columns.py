"""widen world_id columns

Revision ID: f2ad811cb4e9
Revises: 024bcf64747e
Create Date: 2026-06-30 21:37:36.778501

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2ad811cb4e9'
down_revision = '024bcf64747e'
branch_labels = None
depends_on = None


def upgrade():
    for table in ('service_bodies', 'formats', 'meetings'):
        op.alter_column(
            table,
            'world_id',
            existing_type=sa.String(length=20),
            type_=sa.String(length=255),
            existing_nullable=True,
        )


def downgrade():
    for table in ('service_bodies', 'formats', 'meetings'):
        op.alter_column(
            table,
            'world_id',
            existing_type=sa.String(length=255),
            type_=sa.String(length=20),
            existing_nullable=True,
        )
