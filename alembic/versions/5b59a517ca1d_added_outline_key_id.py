"""added outline_key_id

Revision ID: 5b59a517ca1d
Revises: 11a8f17b1592
Create Date: 2024-09-21 09:26:06.300670

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b59a517ca1d'
down_revision: Union[str, None] = '11a8f17b1592'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('subscriptions', 'user_id',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False)
    op.alter_column('transactions', 'user_id',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False)
    op.alter_column('users', 'user_id',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('users', 'tg_id',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False)
    op.add_column('vpn_keys', sa.Column('outline_key_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('vpn_keys', 'outline_key_id')
    op.alter_column('users', 'tg_id',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=False)
    op.alter_column('users', 'user_id',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('transactions', 'user_id',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=False)
    op.alter_column('subscriptions', 'user_id',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=False)
    # ### end Alembic commands ###