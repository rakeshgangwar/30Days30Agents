"""Add owner_id column to personas table

Revision ID: 002
Revises: 001
Create Date: 2025-10-04

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add owner_id column to personas table
    op.add_column('personas', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'personas', 'users', ['owner_id'], ['id'])

def downgrade() -> None:
    # Drop owner_id column from personas table
    op.drop_constraint(op.f('fk_personas_owner_id_users'), 'personas', type_='foreignkey')
    op.drop_column('personas', 'owner_id')
