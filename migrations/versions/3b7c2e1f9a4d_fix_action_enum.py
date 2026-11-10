"""fix action_enum: APPROVED -> ACTIVE

Revision ID: 3b7c2e1f9a4d
Revises: 10f5e6ce23d9
Create Date: 2026-11-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '3b7c2e1f9a4d'
down_revision: Union[str, Sequence[str], None] = '10f5e6ce23d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE action_enum RENAME VALUE 'APPROVED' TO 'ACTIVE'")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TYPE action_enum RENAME VALUE 'ACTIVE' TO 'APPROVED'")
