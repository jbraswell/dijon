"""initial schema

Revision ID: e833cc944cd9
Revises: 
Create Date: 2022-02-03 21:02:27.750833

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e833cc944cd9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('root_servers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('url', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_root_servers_id'), 'root_servers', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('hashed_password', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('format_naws_codes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('root_server_id', sa.Integer(), nullable=False),
    sa.Column('bmlt_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['root_server_id'], ['root_servers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_format_naws_codes_id'), 'format_naws_codes', ['id'], unique=False)
    op.create_table('meeting_naws_codes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('root_server_id', sa.Integer(), nullable=False),
    sa.Column('bmlt_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['root_server_id'], ['root_servers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meeting_naws_codes_id'), 'meeting_naws_codes', ['id'], unique=False)
    op.create_table('service_body_naws_codes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('root_server_id', sa.Integer(), nullable=False),
    sa.Column('bmlt_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['root_server_id'], ['root_servers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_body_naws_codes_id'), 'service_body_naws_codes', ['id'], unique=False)
    op.create_table('snapshots',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('root_server_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['root_server_id'], ['root_servers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_snapshots_id'), 'snapshots', ['id'], unique=False)
    op.create_table('tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=255), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tokens_expires_at'), 'tokens', ['expires_at'], unique=False)
    op.create_index(op.f('ix_tokens_id'), 'tokens', ['id'], unique=False)
    op.create_index(op.f('ix_tokens_token'), 'tokens', ['token'], unique=False)
    op.create_index(op.f('ix_tokens_user_id'), 'tokens', ['user_id'], unique=False)
    op.create_table('formats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('snapshot_id', sa.Integer(), nullable=False),
    sa.Column('bmlt_id', sa.Integer(), nullable=False),
    sa.Column('key_string', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('world_id', sa.String(length=20), nullable=True),
    sa.Column('format_naws_code_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['format_naws_code_id'], ['format_naws_codes.id'], ),
    sa.ForeignKeyConstraint(['snapshot_id'], ['snapshots.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_formats_id'), 'formats', ['id'], unique=False)
    op.create_table('service_bodies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('snapshot_id', sa.Integer(), nullable=False),
    sa.Column('bmlt_id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('type', sa.String(length=20), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('url', sa.String(length=255), nullable=True),
    sa.Column('helpline', sa.String(length=255), nullable=True),
    sa.Column('world_id', sa.String(length=20), nullable=True),
    sa.Column('service_body_naws_code_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['service_bodies.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['service_body_naws_code_id'], ['service_body_naws_codes.id'], ),
    sa.ForeignKeyConstraint(['snapshot_id'], ['snapshots.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_bodies_id'), 'service_bodies', ['id'], unique=False)
    op.create_table('meetings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('snapshot_id', sa.Integer(), nullable=False),
    sa.Column('bmlt_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('day', sa.Enum('SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', name='dayofweekenum'), nullable=False),
    sa.Column('service_body_id', sa.Integer(), nullable=False),
    sa.Column('venue_type', sa.Enum('NONE', 'IN_PERSON', 'VIRTUAL', 'HYBRID', name='venuetypeenum'), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('duration', sa.Interval(), nullable=False),
    sa.Column('time_zone', sa.String(length=255), nullable=True),
    sa.Column('latitude', sa.DECIMAL(precision=15, scale=12), nullable=True),
    sa.Column('longitude', sa.DECIMAL(precision=15, scale=12), nullable=True),
    sa.Column('published', sa.Boolean(), nullable=False),
    sa.Column('world_id', sa.String(length=20), nullable=True),
    sa.Column('meeting_naws_code_id', sa.Integer(), nullable=True),
    sa.Column('location_text', sa.Text(), nullable=True),
    sa.Column('location_info', sa.Text(), nullable=True),
    sa.Column('location_street', sa.Text(), nullable=True),
    sa.Column('location_city_subsection', sa.Text(), nullable=True),
    sa.Column('location_neighborhood', sa.Text(), nullable=True),
    sa.Column('location_municipality', sa.Text(), nullable=True),
    sa.Column('location_sub_province', sa.Text(), nullable=True),
    sa.Column('location_province', sa.Text(), nullable=True),
    sa.Column('location_postal_code_1', sa.Text(), nullable=True),
    sa.Column('location_nation', sa.Text(), nullable=True),
    sa.Column('train_lines', sa.Text(), nullable=True),
    sa.Column('bus_lines', sa.Text(), nullable=True),
    sa.Column('comments', sa.Text(), nullable=True),
    sa.Column('virtual_meeting_link', sa.Text(), nullable=True),
    sa.Column('phone_meeting_number', sa.Text(), nullable=True),
    sa.Column('virtual_meeting_additional_info', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['meeting_naws_code_id'], ['meeting_naws_codes.id'], ),
    sa.ForeignKeyConstraint(['service_body_id'], ['service_bodies.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['snapshot_id'], ['snapshots.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meetings_id'), 'meetings', ['id'], unique=False)
    op.create_table('meeting_formats',
    sa.Column('meeting_id', sa.Integer(), nullable=False),
    sa.Column('format_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['format_id'], ['formats.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('meeting_id', 'format_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('meeting_formats')
    op.drop_index(op.f('ix_meetings_id'), table_name='meetings')
    op.drop_table('meetings')
    op.drop_index(op.f('ix_service_bodies_id'), table_name='service_bodies')
    op.drop_table('service_bodies')
    op.drop_index(op.f('ix_formats_id'), table_name='formats')
    op.drop_table('formats')
    op.drop_index(op.f('ix_tokens_user_id'), table_name='tokens')
    op.drop_index(op.f('ix_tokens_token'), table_name='tokens')
    op.drop_index(op.f('ix_tokens_id'), table_name='tokens')
    op.drop_index(op.f('ix_tokens_expires_at'), table_name='tokens')
    op.drop_table('tokens')
    op.drop_index(op.f('ix_snapshots_id'), table_name='snapshots')
    op.drop_table('snapshots')
    op.drop_index(op.f('ix_service_body_naws_codes_id'), table_name='service_body_naws_codes')
    op.drop_table('service_body_naws_codes')
    op.drop_index(op.f('ix_meeting_naws_codes_id'), table_name='meeting_naws_codes')
    op.drop_table('meeting_naws_codes')
    op.drop_index(op.f('ix_format_naws_codes_id'), table_name='format_naws_codes')
    op.drop_table('format_naws_codes')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_root_servers_id'), table_name='root_servers')
    op.drop_table('root_servers')
    # ### end Alembic commands ###
