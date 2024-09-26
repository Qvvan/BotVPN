"""update servers

Revision ID: 7e783681cd7f
Revises: 091b98d952b2
Create Date: 2024-09-26 11:02:55.965486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e783681cd7f'
down_revision: Union[str, None] = '091b98d952b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('servers', sa.Column('name', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('servers', 'name')
    # ### end Alembic commands ###
