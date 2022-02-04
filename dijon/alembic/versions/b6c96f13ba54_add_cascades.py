"""add cascades

Revision ID: b6c96f13ba54
Revises: 065e0d943491
Create Date: 2022-02-03 20:24:39.241501

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6c96f13ba54'
down_revision = '065e0d943491'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('format_naws_codes_ibfk_1', 'format_naws_codes', type_='foreignkey')
    op.create_foreign_key(None, 'format_naws_codes', 'root_servers', ['root_server_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('service_body_naws_codes_ibfk_1', 'service_body_naws_codes', type_='foreignkey')
    op.create_foreign_key(None, 'service_body_naws_codes', 'root_servers', ['root_server_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'service_body_naws_codes', type_='foreignkey')
    op.create_foreign_key('service_body_naws_codes_ibfk_1', 'service_body_naws_codes', 'root_servers', ['root_server_id'], ['id'])
    op.drop_constraint(None, 'format_naws_codes', type_='foreignkey')
    op.create_foreign_key('format_naws_codes_ibfk_1', 'format_naws_codes', 'root_servers', ['root_server_id'], ['id'])
    # ### end Alembic commands ###