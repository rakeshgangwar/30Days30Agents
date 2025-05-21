"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2023-07-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create personas table
    op.create_table(
        'personas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('background', sa.Text(), nullable=True),
        sa.Column('interests', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('values', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('tone', sa.String(), nullable=True),
        sa.Column('expertise', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('purpose', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_personas_id'), 'personas', ['id'], unique=False)
    op.create_index(op.f('ix_personas_name'), 'personas', ['name'], unique=False)
    op.create_index(op.f('ix_personas_is_active'), 'personas', ['is_active'], unique=False)
    
    # Create platform_connections table
    op.create_table(
        'platform_connections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('persona_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('auth_data', sa.JSON(), nullable=False),
        sa.Column('platform_user_id', sa.String(), nullable=True),
        sa.Column('profile_url', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['persona_id'], ['personas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_platform_connections_id'), 'platform_connections', ['id'], unique=False)
    op.create_index(op.f('ix_platform_connections_persona_id'), 'platform_connections', ['persona_id'], unique=False)
    op.create_index(op.f('ix_platform_connections_platform'), 'platform_connections', ['platform'], unique=False)
    op.create_index(op.f('ix_platform_connections_username'), 'platform_connections', ['username'], unique=False)
    op.create_index(op.f('ix_platform_connections_platform_user_id'), 'platform_connections', ['platform_user_id'], unique=False)
    op.create_index(op.f('ix_platform_connections_is_active'), 'platform_connections', ['is_active'], unique=False)
    
    # Create content table
    op.create_table(
        'content',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('persona_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, default='draft'),
        sa.Column('scheduled_time', sa.DateTime(), nullable=True),
        sa.Column('published_time', sa.DateTime(), nullable=True),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('media_urls', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['persona_id'], ['personas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_id'), 'content', ['id'], unique=False)
    op.create_index(op.f('ix_content_persona_id'), 'content', ['persona_id'], unique=False)
    op.create_index(op.f('ix_content_content_type'), 'content', ['content_type'], unique=False)
    op.create_index(op.f('ix_content_platform'), 'content', ['platform'], unique=False)
    op.create_index(op.f('ix_content_status'), 'content', ['status'], unique=False)
    op.create_index(op.f('ix_content_scheduled_time'), 'content', ['scheduled_time'], unique=False)
    op.create_index(op.f('ix_content_external_id'), 'content', ['external_id'], unique=False)
    
    # Create interactions table
    op.create_table(
        'interactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('persona_id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=True),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('interaction_type', sa.String(), nullable=False),
        sa.Column('external_id', sa.String(), nullable=False),
        sa.Column('external_user_id', sa.String(), nullable=False),
        sa.Column('external_username', sa.String(), nullable=False),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('sentiment', sa.String(), nullable=True),
        sa.Column('is_processed', sa.Boolean(), nullable=True, default=False),
        sa.Column('response_id', sa.Integer(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['content_id'], ['content.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['persona_id'], ['personas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['response_id'], ['content.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interactions_id'), 'interactions', ['id'], unique=False)
    op.create_index(op.f('ix_interactions_persona_id'), 'interactions', ['persona_id'], unique=False)
    op.create_index(op.f('ix_interactions_content_id'), 'interactions', ['content_id'], unique=False)
    op.create_index(op.f('ix_interactions_platform'), 'interactions', ['platform'], unique=False)
    op.create_index(op.f('ix_interactions_interaction_type'), 'interactions', ['interaction_type'], unique=False)
    op.create_index(op.f('ix_interactions_external_id'), 'interactions', ['external_id'], unique=False)
    op.create_index(op.f('ix_interactions_external_user_id'), 'interactions', ['external_user_id'], unique=False)
    op.create_index(op.f('ix_interactions_external_username'), 'interactions', ['external_username'], unique=False)
    op.create_index(op.f('ix_interactions_sentiment'), 'interactions', ['sentiment'], unique=False)
    op.create_index(op.f('ix_interactions_is_processed'), 'interactions', ['is_processed'], unique=False)
    op.create_index(op.f('ix_interactions_response_id'), 'interactions', ['response_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('interactions')
    op.drop_table('content')
    op.drop_table('platform_connections')
    op.drop_table('personas')
