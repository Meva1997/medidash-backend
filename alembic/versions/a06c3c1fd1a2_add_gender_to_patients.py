"""add_gender_to_patients

Revision ID: a06c3c1fd1a2
Revises: b6b9c614bd18
Create Date: 2026-04-25 09:24:36.076357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a06c3c1fd1a2'
down_revision: Union[str, Sequence[str], None] = 'b6b9c614bd18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


gender_enum = sa.Enum('male', 'female', 'other', name='genderenum')

def upgrade() -> None:
    """Upgrade schema."""
    gender_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('patients', sa.Column('gender', gender_enum, nullable=True))
    op.execute("UPDATE patients SET gender = 'other' WHERE gender IS NULL")
    op.alter_column('patients', 'gender', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('patients', 'gender')
    gender_enum.drop(op.get_bind(), checkfirst=True)
