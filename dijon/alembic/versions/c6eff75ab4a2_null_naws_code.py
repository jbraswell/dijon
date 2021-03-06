"""null naws code

Revision ID: c6eff75ab4a2
Revises: e833cc944cd9
Create Date: 2022-02-09 12:17:29.220554

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6eff75ab4a2'
down_revision = 'e833cc944cd9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('format_naws_codes', sa.Column('code', sa.String(length=20), nullable=False))
    op.add_column('format_naws_codes', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('format_naws_codes', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.drop_constraint('formats_ibfk_1', 'formats', type_='foreignkey')
    op.create_foreign_key(None, 'formats', 'format_naws_codes', ['format_naws_code_id'], ['id'], ondelete='SET NULL')
    op.add_column('meeting_naws_codes', sa.Column('code', sa.String(length=20), nullable=False))
    op.drop_constraint('meetings_ibfk_1', 'meetings', type_='foreignkey')
    op.create_foreign_key(None, 'meetings', 'meeting_naws_codes', ['meeting_naws_code_id'], ['id'], ondelete='SET NULL')
    op.drop_constraint('service_bodies_ibfk_2', 'service_bodies', type_='foreignkey')
    op.create_foreign_key(None, 'service_bodies', 'service_body_naws_codes', ['service_body_naws_code_id'], ['id'], ondelete='SET NULL')
    op.add_column('service_body_naws_codes', sa.Column('code', sa.String(length=20), nullable=False))
    op.add_column('service_body_naws_codes', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('service_body_naws_codes', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('service_body_naws_codes', 'updated_at')
    op.drop_column('service_body_naws_codes', 'created_at')
    op.drop_column('service_body_naws_codes', 'code')
    op.drop_constraint(None, 'service_bodies', type_='foreignkey')
    op.create_foreign_key('service_bodies_ibfk_2', 'service_bodies', 'service_body_naws_codes', ['service_body_naws_code_id'], ['id'])
    op.drop_constraint(None, 'meetings', type_='foreignkey')
    op.create_foreign_key('meetings_ibfk_1', 'meetings', 'meeting_naws_codes', ['meeting_naws_code_id'], ['id'])
    op.drop_column('meeting_naws_codes', 'code')
    op.drop_constraint(None, 'formats', type_='foreignkey')
    op.create_foreign_key('formats_ibfk_1', 'formats', 'format_naws_codes', ['format_naws_code_id'], ['id'])
    op.drop_column('format_naws_codes', 'updated_at')
    op.drop_column('format_naws_codes', 'created_at')
    op.drop_column('format_naws_codes', 'code')
    # ### end Alembic commands ###
