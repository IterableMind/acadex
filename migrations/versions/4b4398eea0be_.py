"""empty message

Revision ID: 4b4398eea0be
Revises: 53c1c1e70853
Create Date: 2025-03-01 01:38:03.087907

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b4398eea0be'
down_revision = '53c1c1e70853'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_subject')
    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.drop_constraint('uq_roles_teacher_id', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_roles_teacher_id', ['teacher_id'])

    op.create_table('_alembic_tmp_subject',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('fullname', sa.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
