"""remove awkward fk

Revision ID: 83055e112b14
Revises: 52279bdc848c
Create Date: 2022-02-09 15:11:33.900788

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '83055e112b14'
down_revision = '52279bdc848c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('formats_ibfk_3', 'formats', type_='foreignkey')
    op.drop_column('formats', 'format_naws_code_id')
    op.drop_constraint('meetings_ibfk_4', 'meetings', type_='foreignkey')
    op.drop_column('meetings', 'meeting_naws_code_id')
    op.drop_constraint('service_bodies_ibfk_4', 'service_bodies', type_='foreignkey')
    op.drop_column('service_bodies', 'service_body_naws_code_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_bodies', sa.Column('service_body_naws_code_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('service_bodies_ibfk_4', 'service_bodies', 'service_body_naws_codes', ['service_body_naws_code_id'], ['id'], ondelete='SET NULL')
    op.add_column('meetings', sa.Column('meeting_naws_code_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('meetings_ibfk_4', 'meetings', 'meeting_naws_codes', ['meeting_naws_code_id'], ['id'], ondelete='SET NULL')
    op.add_column('formats', sa.Column('format_naws_code_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('formats_ibfk_3', 'formats', 'format_naws_codes', ['format_naws_code_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###
