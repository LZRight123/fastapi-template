"""2024-12-06 初始化调整

Revision ID: 57e28e9449f7
Revises: 
Create Date: 2024-12-06 12:22:17.469884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '57e28e9449f7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('loginrequestrecord',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sms_code_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('code', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('ip_address', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sms_code_records_ip_address'), 'sms_code_records', ['ip_address'], unique=False)
    op.create_index(op.f('ix_sms_code_records_phone'), 'sms_code_records', ['phone'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('phone', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('invite_code', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_invite_code'), 'user', ['invite_code'], unique=True)
    op.create_index(op.f('ix_user_phone'), 'user', ['phone'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_phone'), table_name='user')
    op.drop_index(op.f('ix_user_invite_code'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_sms_code_records_phone'), table_name='sms_code_records')
    op.drop_index(op.f('ix_sms_code_records_ip_address'), table_name='sms_code_records')
    op.drop_table('sms_code_records')
    op.drop_table('loginrequestrecord')
    # ### end Alembic commands ###
