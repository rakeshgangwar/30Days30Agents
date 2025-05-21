"""Consolidated schema reflecting current models

Revision ID: 004_consolidated_schema
Revises: 
Create Date: 2025-04-10 21:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_consolidated_schema'
down_revision = None # Represents the base state (no tables)
branch_labels = None
depends_on = None


def upgrade() -> None:
    print("Creating all tables based on consolidated schema...")

    # ### commands to create all tables ###
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.true(), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), server_default=sa.false(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_full_name'), 'users', ['full_name'], unique=False)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    op.create_table('personas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('background', sa.Text(), nullable=True),
        sa.Column('interests', sa.JSON(), nullable=True),
        sa.Column('values', sa.JSON(), nullable=True),
        sa.Column('tone', sa.String(), nullable=True),
        sa.Column('expertise', sa.JSON(), nullable=True),
        sa.Column('purpose', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.true(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=True), # Added in 002
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_personas_owner_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_personas'))
    )
    op.create_index(op.f('ix_personas_id'), 'personas', ['id'], unique=False)
    op.create_index(op.f('ix_personas_name'), 'personas', ['name'], unique=False)
    op.create_index(op.f('ix_personas_owner_id'), 'personas', ['owner_id'], unique=False) # Index for FK

    op.create_table('content',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('persona_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('status', sa.String(), server_default='draft', nullable=False),
        sa.Column('scheduled_time', sa.DateTime(), nullable=True),
        sa.Column('published_time', sa.DateTime(), nullable=True),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('media_urls', sa.JSON(), nullable=True),
        sa.Column('content_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['persona_id'], ['personas.id'], name=op.f('fk_content_persona_id_personas')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_content'))
    )
    op.create_index(op.f('ix_content_content_type'), 'content', ['content_type'], unique=False)
    op.create_index(op.f('ix_content_external_id'), 'content', ['external_id'], unique=False)
    op.create_index(op.f('ix_content_id'), 'content', ['id'], unique=False)
    op.create_index(op.f('ix_content_persona_id'), 'content', ['persona_id'], unique=False)
    op.create_index(op.f('ix_content_platform'), 'content', ['platform'], unique=False)
    op.create_index(op.f('ix_content_scheduled_time'), 'content', ['scheduled_time'], unique=False)
    op.create_index(op.f('ix_content_status'), 'content', ['status'], unique=False)

    op.create_table('platform_connections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('persona_id', sa.Integer(), nullable=False),
        sa.Column('platform_name', sa.String(), nullable=False), # Correct name
        sa.Column('platform_id', sa.String(), nullable=False),   # Correct name
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('credentials', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('platform_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['persona_id'], ['personas.id'], name=op.f('fk_platform_connections_persona_id_personas'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_platform_connections'))
    )
    op.create_index(op.f('ix_platform_connections_id'), 'platform_connections', ['id'], unique=False)
    op.create_index(op.f('ix_platform_connections_persona_id'), 'platform_connections', ['persona_id'], unique=False)
    op.create_index(op.f('ix_platform_connections_platform_name'), 'platform_connections', ['platform_name'], unique=False) # Correct index
    op.create_index(op.f('ix_platform_connections_username'), 'platform_connections', ['username'], unique=False)

    op.create_table('interactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('persona_id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=True), # Added
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('external_id', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=False), # Renamed from content
        sa.Column('author_data', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(), server_default='pending', nullable=False),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('platform_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('responded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['persona_id'], ['personas.id'], name=op.f('fk_interactions_persona_id_personas'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['content_id'], ['content.id'], name=op.f('fk_interactions_content_id_content'), ondelete='CASCADE'), # Added FK
        sa.PrimaryKeyConstraint('id', name=op.f('pk_interactions'))
    )
    op.create_index(op.f('ix_interactions_id'), 'interactions', ['id'], unique=False)
    op.create_index(op.f('ix_interactions_persona_id'), 'interactions', ['persona_id'], unique=False)
    op.create_index(op.f('ix_interactions_content_id'), 'interactions', ['content_id'], unique=False) # Added index
    op.create_index(op.f('ix_interactions_platform'), 'interactions', ['platform'], unique=False)
    op.create_index(op.f('ix_interactions_external_id'), 'interactions', ['external_id'], unique=False)
    op.create_index(op.f('ix_interactions_type'), 'interactions', ['type'], unique=False)
    op.create_index(op.f('ix_interactions_status'), 'interactions', ['status'], unique=False)
    op.create_index(op.f('ix_interactions_created_at'), 'interactions', ['created_at'], unique=False)

    print("Finished creating tables.")
    # ### end Alembic commands ###


def downgrade() -> None:
    print("Dropping all tables...")
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_interactions_created_at'), table_name='interactions')
    op.drop_index(op.f('ix_interactions_status'), table_name='interactions')
    op.drop_index(op.f('ix_interactions_type'), table_name='interactions')
    op.drop_index(op.f('ix_interactions_external_id'), table_name='interactions')
    op.drop_index(op.f('ix_interactions_platform'), table_name='interactions')
    op.drop_index(op.f('ix_interactions_content_id'), table_name='interactions')
    op.drop_index(op.f('ix_interactions_persona_id'), table_name='interactions')
    op.drop_index(op.f('ix_interactions_id'), table_name='interactions')
    op.drop_table('interactions')

    op.drop_index(op.f('ix_platform_connections_username'), table_name='platform_connections')
    op.drop_index(op.f('ix_platform_connections_platform_name'), table_name='platform_connections')
    op.drop_index(op.f('ix_platform_connections_persona_id'), table_name='platform_connections')
    op.drop_index(op.f('ix_platform_connections_id'), table_name='platform_connections')
    op.drop_table('platform_connections')

    op.drop_index(op.f('ix_content_status'), table_name='content')
    op.drop_index(op.f('ix_content_scheduled_time'), table_name='content')
    op.drop_index(op.f('ix_content_platform'), table_name='content')
    op.drop_index(op.f('ix_content_persona_id'), table_name='content')
    op.drop_index(op.f('ix_content_id'), table_name='content')
    op.drop_index(op.f('ix_content_external_id'), table_name='content')
    op.drop_index(op.f('ix_content_content_type'), table_name='content')
    op.drop_table('content')

    op.drop_index(op.f('ix_personas_owner_id'), table_name='personas')
    op.drop_index(op.f('ix_personas_name'), table_name='personas')
    op.drop_index(op.f('ix_personas_id'), table_name='personas')
    op.drop_table('personas')

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_full_name'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    print("Finished dropping tables.")
    # ### end Alembic commands ###