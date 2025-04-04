"""Fix database schema mismatches

Revision ID: 5d30f49f0bd2
Revises: 
Create Date: 2025-03-06 01:51:29.239980

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5d30f49f0bd2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('last_active',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('now()'))
        batch_op.alter_column('password_history',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=False,
               existing_server_default=sa.text("'[]'::json"))
        batch_op.alter_column('password_last_changed',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text('now()'))
        batch_op.drop_constraint('user_password_reset_token_key', type_='unique')
        batch_op.drop_column('reset_token_expiry')
        batch_op.drop_column('password_reset_token')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_reset_token', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('reset_token_expiry', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.create_unique_constraint('user_password_reset_token_key', ['password_reset_token'])
        batch_op.alter_column('password_last_changed',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('now()'))
        batch_op.alter_column('password_history',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=True,
               existing_server_default=sa.text("'[]'::json"))
        batch_op.alter_column('last_active',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text('now()'))

    # ### end Alembic commands ###
