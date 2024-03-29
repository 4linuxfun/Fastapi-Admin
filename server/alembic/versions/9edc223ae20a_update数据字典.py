"""update数据字典

Revision ID: 9edc223ae20a
Revises: 001da528b756
Create Date: 2022-11-11 10:57:04.750421

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9edc223ae20a'
down_revision = '001da528b756'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dict_item', sa.Column('label', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False, comment='名称'))
    op.add_column('dict_item', sa.Column('value', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False, comment='数据值'))
    op.drop_column('dict_item', 'data')
    op.drop_column('dict_item', 'name')
    op.alter_column('menu', 'icon',
               existing_type=mysql.VARCHAR(collation='utf8mb4_general_ci', length=50),
               nullable=True,
               existing_comment='Icon图标')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('menu', 'icon',
               existing_type=mysql.VARCHAR(collation='utf8mb4_general_ci', length=50),
               nullable=False,
               existing_comment='Icon图标')
    op.add_column('dict_item', sa.Column('name', mysql.VARCHAR(collation='utf8mb4_general_ci', length=50), nullable=False, comment='名称'))
    op.add_column('dict_item', sa.Column('data', mysql.VARCHAR(collation='utf8mb4_general_ci', length=100), nullable=False, comment='数据值'))
    op.drop_column('dict_item', 'value')
    op.drop_column('dict_item', 'label')
    # ### end Alembic commands ###
