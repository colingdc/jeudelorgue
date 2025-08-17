"""Remove roles table

Revision ID: 7085ac4dec7a
Revises: c88d801582e5
Create Date: 2025-08-17 08:35:08.471472

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7085ac4dec7a'
down_revision = 'c88d801582e5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('users_ibfk_1', type_='foreignkey')

    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.drop_index('ix_roles_default')
        batch_op.drop_index('name')

    op.drop_table('roles')


def downgrade():
    op.create_table(
        'roles',
        sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
        sa.Column('name', mysql.VARCHAR(collation='utf8mb4_general_ci', length=64), nullable=True),
        sa.Column('default', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
        sa.Column('permissions', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
        sa.CheckConstraint('(`default` in (0,1))', name='roles_chk_1'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_general_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )

    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.create_index('name', ['name'], unique=False)
        batch_op.create_index('ix_roles_default', ['default'], unique=False)

    op.execute("""
        INSERT INTO roles (id, name, `default`) VALUES 
        (1, 'User', 1),
        (2, 'Manager', 0),
        (3, 'Administrator', 0)
    """)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_foreign_key('users_ibfk_1', 'roles', ['role_id'], ['id'])
