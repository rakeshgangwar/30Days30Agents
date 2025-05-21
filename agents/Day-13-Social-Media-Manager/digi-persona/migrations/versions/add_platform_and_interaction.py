"""Add platform and interaction models

Revision ID: 003
Revises: 002
Create Date: 2025-10-04

"""
from typing import Sequence, Union, List
import sqlalchemy as sa
from sqlalchemy.engine import reflection
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def _get_inspector():
    bind = op.get_bind()
    return reflection.Inspector.from_engine(bind)

def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    inspector = _get_inspector()
    return table_name in inspector.get_table_names()

def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    if not table_exists(table_name):
        return False
    inspector = _get_inspector()
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def upgrade() -> None:
    bind = op.get_bind()
    inspector = reflection.Inspector.from_engine(bind)

    # --- platform_connections table ---
    if not table_exists('platform_connections'):
        op.create_table(
            'platform_connections',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('persona_id', sa.Integer(), nullable=False),
            sa.Column('platform_name', sa.String(), nullable=False), # Added
            sa.Column('platform_id', sa.String(), nullable=False),
            sa.Column('username', sa.String(), nullable=False),
            sa.Column('credentials', sa.JSON(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column('platform_metadata', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.ForeignKeyConstraint(['persona_id'], ['personas.id'], name=op.f('fk_platform_connections_persona_id_personas'), ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id', name=op.f('pk_platform_connections'))
        )
        op.create_index(op.f('ix_platform_connections_id'), 'platform_connections', ['id'], unique=False)
        op.create_index(op.f('ix_platform_connections_platform_name'), 'platform_connections', ['platform_name'], unique=False) # Added index
        op.create_index(op.f('ix_platform_connections_persona_id'), 'platform_connections', ['persona_id'], unique=False)
        print("Created platform_connections table")
    else:
        print("platform_connections table already exists.")
        # Add platform_name column if it doesn't exist
        if not column_exists('platform_connections', 'platform_name'):
            op.add_column('platform_connections', sa.Column('platform_name', sa.String(), nullable=False, server_default='unknown')) # Add default temporarily
            # Update existing rows if needed, then remove server_default if appropriate
            # For simplicity, we assume new rows will provide it, or handle default in application logic
            op.alter_column('platform_connections', 'platform_name', server_default=None)
            op.create_index(op.f('ix_platform_connections_platform_name'), 'platform_connections', ['platform_name'], unique=False)
            print("Added platform_name column and index to platform_connections")

    # --- interactions table ---
    if not table_exists('interactions'):
        op.create_table(
            'interactions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('persona_id', sa.Integer(), nullable=False),
            sa.Column('content_id', sa.Integer(), nullable=True), # Added
            sa.Column('platform', sa.String(), nullable=False),
            sa.Column('external_id', sa.String(), nullable=False),
            sa.Column('type', sa.String(), nullable=False),
            sa.Column('content_text', sa.Text(), nullable=False), # Renamed from content
            sa.Column('author_data', sa.JSON(), nullable=False),
            sa.Column('status', sa.String(), nullable=False, server_default='pending'),
            sa.Column('response', sa.Text(), nullable=True),
            sa.Column('platform_data', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
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
        print("Created interactions table")
    else:
        print("interactions table already exists.")
        # Add content_id column if it doesn't exist
        if not column_exists('interactions', 'content_id'):
            op.add_column('interactions', sa.Column('content_id', sa.Integer(), nullable=True))
            op.create_foreign_key(
                op.f('fk_interactions_content_id_content'),
                'interactions', 'content', ['content_id'], ['id'], ondelete='CASCADE'
            )
            op.create_index(op.f('ix_interactions_content_id'), 'interactions', ['content_id'], unique=False)
            print("Added content_id column, FK, and index to interactions")

        # Handle content -> content_text rename/addition
        has_content = column_exists('interactions', 'content')
        has_content_text = column_exists('interactions', 'content_text')

        if has_content and not has_content_text:
            op.alter_column('interactions', 'content', new_column_name='content_text', existing_type=sa.Text(), nullable=False)
            print("Renamed content column to content_text in interactions")
        elif not has_content and not has_content_text:
            op.add_column('interactions', sa.Column('content_text', sa.Text(), nullable=False, server_default='')) # Add default temporarily
            op.alter_column('interactions', 'content_text', server_default=None)
            print("Added content_text column to interactions")
        elif has_content and has_content_text:
             # Both exist, maybe drop the old 'content' if safe, or just log
             print("Warning: Both 'content' and 'content_text' columns exist in interactions. Consider cleanup.")
             # op.drop_column('interactions', 'content') # Optional: Drop old column if sure

        # Add other potentially missing columns (idempotent checks)
        if not column_exists('interactions', 'platform'): op.add_column('interactions', sa.Column('platform', sa.String(), nullable=False, server_default='unknown')); op.alter_column('interactions', 'platform', server_default=None); print("Added platform column")
        if not column_exists('interactions', 'external_id'): op.add_column('interactions', sa.Column('external_id', sa.String(), nullable=False, server_default='unknown')); op.alter_column('interactions', 'external_id', server_default=None); print("Added external_id column")
        if not column_exists('interactions', 'type'): op.add_column('interactions', sa.Column('type', sa.String(), nullable=False, server_default='unknown')); op.alter_column('interactions', 'type', server_default=None); print("Added type column")
        if not column_exists('interactions', 'author_data'): op.add_column('interactions', sa.Column('author_data', sa.JSON(), nullable=False, server_default='{}')); op.alter_column('interactions', 'author_data', server_default=None); print("Added author_data column")
        if not column_exists('interactions', 'status'): op.add_column('interactions', sa.Column('status', sa.String(), nullable=False, server_default='pending')); op.alter_column('interactions', 'status', server_default=None); print("Added status column")
        if not column_exists('interactions', 'response'): op.add_column('interactions', sa.Column('response', sa.Text(), nullable=True)); print("Added response column")
        if not column_exists('interactions', 'platform_data'): op.add_column('interactions', sa.Column('platform_data', sa.JSON(), nullable=True)); print("Added platform_data column")
        if not column_exists('interactions', 'created_at'): op.add_column('interactions', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())); op.alter_column('interactions', 'created_at', server_default=None); print("Added created_at column")
        if not column_exists('interactions', 'updated_at'): op.add_column('interactions', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())); op.alter_column('interactions', 'updated_at', server_default=None); print("Added updated_at column")
        if not column_exists('interactions', 'responded_at'): op.add_column('interactions', sa.Column('responded_at', sa.DateTime(), nullable=True)); print("Added responded_at column")

        # Add missing indexes
        inspector = _get_inspector()
        indexes = [idx['name'] for idx in inspector.get_indexes('interactions')]
        if op.f('ix_interactions_platform') not in indexes: op.create_index(op.f('ix_interactions_platform'), 'interactions', ['platform'], unique=False)
        if op.f('ix_interactions_external_id') not in indexes: op.create_index(op.f('ix_interactions_external_id'), 'interactions', ['external_id'], unique=False)
        if op.f('ix_interactions_type') not in indexes: op.create_index(op.f('ix_interactions_type'), 'interactions', ['type'], unique=False)
        if op.f('ix_interactions_status') not in indexes: op.create_index(op.f('ix_interactions_status'), 'interactions', ['status'], unique=False)
        if op.f('ix_interactions_created_at') not in indexes: op.create_index(op.f('ix_interactions_created_at'), 'interactions', ['created_at'], unique=False)

def downgrade() -> None:
    """Revert changes made in the upgrade function."""
    # Since the upgrade is designed to be idempotent and primarily adds things,
    # a simple downgrade might just involve dropping the tables if they were created
    # by this migration originally. However, given the complexity and potential
    # for partial states, a safer approach for this specific scenario (forcing re-run)
    # is to make the downgrade a no-op.
    # If a full revert is needed, the logic would mirror the additions in reverse.
    print("Downgrade for 003 is currently a no-op to facilitate re-running upgrade.")
    pass