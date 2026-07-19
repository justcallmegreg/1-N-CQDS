# 0001_initial.py — creates the items table.
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None

def upgrade():
    op.create_table("items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False))

def downgrade():
    op.drop_table("items")
